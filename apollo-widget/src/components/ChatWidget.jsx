// ChatWidget.jsx

import React, { useState, useEffect, useRef, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useChatSocket } from "../hooks/useChatSocket";
import defaultConfig from "../apollo_config";
import "./ChatWidget.css";
import { defaultQuestions, projectQuestions } from "../sample_questions";

function getGuestId() {
  let guestId = localStorage.getItem("guestId");
  if (!guestId) {
    guestId = "guest" + Math.floor(1e9 + Math.random() * 9e9);
    localStorage.setItem("guestId", guestId);
  }
  return guestId;
}

export default function ChatWidget({ config: userConfig }) {
  const cfg = { ...defaultConfig, ...userConfig };

  // inside ChatWidget()
  const currentUrl = window.location.href;
  const projectEntry = Object.values(projectQuestions)
    .find(p => currentUrl.includes(p.url));
  const allQuestions = projectEntry
    ? projectEntry.questions
    : defaultQuestions;

  const triggerCount = Number.isInteger(cfg.showNumberOfQuestions)
    ? cfg.showNumberOfQuestions
    : 3;
  const triggerMobileCount = Number.isInteger(cfg.collectMobileAfterNumberOfQuestion)
    ? cfg.collectMobileAfterNumberOfQuestion
    : 3;
  // — Chat state —
  const [chatHistory, setChatHistory] = useState([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);

  // — Suggestions state —
  const [usedQuestions, setUsedQuestions] = useState([]);
  const [suggestions, setSuggestions] = useState(
    allQuestions.slice(0, triggerCount)
  );

  // — UI state —
  const [fullScreen, setFullScreen] = useState(false);

  // — Phone‐form state —
  const [showPhoneForm, setShowPhoneForm] = useState(false);
  const [phoneFormRequirementsMet, setPhoneFormRequirementsMet] =
    useState(false);
  const [phone, setPhone] = useState("");
  const [phoneFormSubmitted, setPhoneFormSubmitted] = useState(false);
  const [phoneError, setPhoneError] = useState("");

  const chatEndRef = useRef(null);
  const contentRef = useRef(null);
  const [isThinking, setIsThinking] = useState(false);
  const { ws, waitForConnection } = useChatSocket(
    setChatHistory,
    setStreaming,
    setIsThinking
  );

  // 1) Seed system message
  useEffect(() => {
    setChatHistory([{ role: "system", text: cfg.introductionText }]);
  }, [cfg.introductionText]);

  // 2) Auto‐scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, suggestions, showPhoneForm]);

  // 3) Clear suggestions on streaming
  useEffect(() => {
    if (streaming) setSuggestions([]);
  }, [streaming]);

  // 4) Show suggestions 2s after assistant reply
  useEffect(() => {
    let t;
    if (!streaming && chatHistory.some((m) => m.role === "assistant")) {
      t = setTimeout(() => {
        const remaining = allQuestions.filter(
          (q) => !usedQuestions.includes(q)
        );
        setSuggestions(remaining.slice(0, triggerCount));
      }, 2000);
    }
    return () => clearTimeout(t);
  }, [streaming, chatHistory, usedQuestions, allQuestions, triggerCount]);

  // 5) Scroll trapping (unchanged)
  const handleWheel = useCallback((e) => {
    e.stopPropagation();
    const pane = contentRef.current;
    if (!pane) return;
    const atTop = pane.scrollTop === 0 && e.deltaY < 0;
    const atBottom =
      pane.scrollTop + pane.clientHeight >= pane.scrollHeight && e.deltaY > 0;
    if (atTop || atBottom) e.preventDefault();
  }, []);
  const handleTouchMove = useCallback((e) => {
    e.stopPropagation();
    const pane = contentRef.current;
    if (!pane) return;
    const tY = e.touches[0].clientY;
    pane._lastTouchY = pane._lastTouchY || tY;
    const deltaY = pane._lastTouchY - tY;
    pane._lastTouchY = tY;
    const atTop = pane.scrollTop === 0 && deltaY < 0;
    const atBottom =
      pane.scrollTop + pane.clientHeight >= pane.scrollHeight && deltaY > 0;
    if (atTop || atBottom) e.preventDefault();
  }, []);
  useEffect(() => {
    const pane = contentRef.current;
    if (pane) {
      pane.addEventListener("wheel", handleWheel, {
        passive: false,
        capture: true,
      });
      pane.addEventListener("touchmove", handleTouchMove, { passive: false });
      return () => {
        pane.removeEventListener("wheel", handleWheel, { capture: true });
        pane.removeEventListener("touchmove", handleTouchMove);
      };
    }
  }, [handleWheel, handleTouchMove]);

  // 6) Check if requirements for showing phone form are met
  useEffect(() => {
    if (phoneFormSubmitted) return;

    const assistantCount = chatHistory.filter(
      (m) => m.role === "assistant"
    ).length;
    const userCount = chatHistory.filter((m) => m.role === "user").length;

    if (assistantCount >= triggerMobileCount && userCount >= triggerMobileCount - 1) {
      setPhoneFormRequirementsMet(true);
    }
  }, [chatHistory, phoneFormSubmitted, triggerMobileCount]);

  // 7) Handle phone form visibility (similar to suggestions)
  useEffect(() => {
    // Always hide during streaming
    if (streaming) {
      setShowPhoneForm(false);
      return;
    }

    // Show with delay after streaming ends if requirements are met
    if (phoneFormRequirementsMet && !phoneFormSubmitted && !streaming) {
      const timer = setTimeout(() => {
        setShowPhoneForm(true);
      }, 3000); // Show 1s after suggestions
      return () => clearTimeout(timer);
    }
  }, [streaming, phoneFormRequirementsMet, phoneFormSubmitted]);

  // Send a chat message
  const sendToChat = useCallback(async (text) => {
      const guestId = getGuestId();
      setChatHistory((h) => [...h, { role: "user", text }]);
      ws.current.send(
        JSON.stringify({
          user_input: text,
          user_id: guestId,
          agent_key:    cfg.agentKey,
          agent_name: cfg.agentName,
          project_name: cfg.projectName,
          page_url:     cfg.pageUrl || window.location.href,
        })
      );
      setIsThinking(true);
      setStreaming(true);
    },
    [cfg.agentName, cfg.projectName, ws, setIsThinking, setStreaming]
  );

  // Handle suggestion click
  const handleSuggestion = (q) => {
    sendToChat(q);
    setUsedQuestions((u) => [...u, q]);
  };

  // Enter key = send
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        sendToChat(input);
        setInput("");
      }
    }
  };

  // Handle phone form submission (now async so we can await the API call)
  const handlePhoneSubmit = async (e) => {
    e.preventDefault();

    if (phone.length !== 10) {
      setPhoneError("Please enter a valid 10-digit mobile number");
      return;
    }

    // 1️⃣ send into the chat UI:
    const phoneMsg = `My phone number is ${phone}`;
    sendToChat(phoneMsg);

    // 2️⃣ snapshot the full history (including this phone message)
    const fullHistory = [...chatHistory, { role: "user", text: phoneMsg }];

    // 3️⃣ POST to your API endpoint
    try {
      await fetch(cfg.phoneSubmitUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_key: cfg.agentKey,
          agent_name: cfg.agentName,
          mobile: phone,
          project_name: cfg.projectName,
          page_url: cfg.pageUrl || window.location.href,
          chatHistory: fullHistory,
        }),
      });
    } catch (err) {
      console.error("Failed to submit phone + history:", err);
      // optionally set an error state here
    }

    // 4️⃣ hide the form forever and reset
    setShowPhoneForm(false);
    setPhoneFormSubmitted(true);
    setPhone("");
    setPhoneError("");
  };

  const [systemMsg, ...otherMsgs] = chatHistory;
  const toggleFullScreen = () => setFullScreen((f) => !f);

  return (
    <div
      id="chatbot"
      className={`chat-widget${fullScreen ? " fullscreen" : ""}`}
      style={{ "--primary-color": cfg.primaryColor }}
    >
      <div className="chat-wrapper">
        {/* Header */}
        <div className="chat-header">
          <img
            src={cfg.companyLogo}
            alt={`${cfg.companyName} logo`}
            className="chat-logo"
          />
          <h2 className="chat-title">{cfg.companyName} AI Agent</h2>
          <div className="header-buttons">
            <button onClick={toggleFullScreen} className="fullscreen-button">
              {fullScreen ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M8 3v3a2 2 0 0 1-2 2H3" />
                  <path d="M21 8h-3a2 2 0 0 1-2-2V3" />
                  <path d="M3 16h3a2 2 0 0 1 2 2v3" />
                  <path d="M16 21v-3a2 2 0 0 1 2-2h3" />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M8 3H5a2 2 0 0 0-2 2v3" />
                  <path d="M21 8V5a2 2 0 0 0-2-2h-3" />
                  <path d="M3 16v3a2 2 0 0 0 2 2h3" />
                  <path d="M16 21h3a2 2 0 0 0 2-2v-3" />
                </svg>
              )}
            </button>
            <button
              onClick={() => {
                const chatbot = document.getElementById("chatbot");
                const button = document.getElementById("elan-ai-button");

                if (chatbot) {
                  chatbot.style.display = "none";
                  chatbot.classList.add("hidden");
                }

                if (button) {
                  button.style.display = "block";
                  button.classList.remove("hidden");
                }
              }}
              className="close-button"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>

        {/* Chat History */}
        <div className="chat-content" ref={contentRef}>
          {systemMsg && (
            <div className="chat-block system">
              <div className="message">
                <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
                  {systemMsg.text}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {otherMsgs.map((msg, i) => (
            <div key={i} className={`chat-block ${msg.role}`}>
              {msg.role === "assistant" && (
                <div className="message-label">{`${cfg.companyName} AI Agent`}</div>
              )}
              <div className="message">
                <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
                  {msg.text}
                </ReactMarkdown>
              </div>
            </div>
          ))}

          {/* Suggestions */}
          {!streaming && suggestions.length > 0 && (
            <div className="suggestions">
              {suggestions.map((q, i) => (
                <button
                  key={i}
                  className="suggestion-button"
                  onClick={() => handleSuggestion(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Phone-number capture form */}
          {showPhoneForm && !streaming && (
            <div className="phone-form" id="phoneFormContainer">
              <div className="phone-form__body">
                <div className="phone-form__details">
                  <label className="phone-form__label">
                    To enable our expert to help, please enter your contact number:
                  </label>
                  <form
                    className="phone-form__form"
                    onSubmit={handlePhoneSubmit}
                  >
                    {phoneError && (
                      <div className="phone-form__error">{phoneError}</div>
                    )}
                    <div className="phone-form__input-container">
                      <input
                        className="phone-form__input"
                        type="tel"
                        placeholder="Your Mobile Number Please"
                        maxLength={10}
                        value={phone}
                        onChange={(e) => {
                          setPhone(e.target.value.replace(/\D/, ""));
                          setPhoneError(""); // clear error on change
                        }}
                      />
                      <button type="submit" className="phone-form__submit">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          width="16"
                          height="16"
                        >
                          <path
                            fill="#ffffff"
                            d="M22,11.7V12h-0.1c-0.1,1-17.7,9.5-18.8,9.1c-1.1-0.4,2.4-6.7,3-7.5C6.8,12.9,17.1,12,17.1,12H17c0,0,0-0.2,0-0.2c0,0,0,0,0,0c0-0.4-10.2-1-10.8-1.7c-0.6-0.7-4-7.1-3-7.5C4.3,2.1,22,10.5,22,11.7z"
                          ></path>
                        </svg>
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          )}

          {/* Typing indicator */}
          {isThinking && (
            <div className="chat-block assistant">
              <div className="message-label">{`${cfg.companyName} AI Agent`}</div>
              <div className="message typing-indicator">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar (unchanged) */}
        <div className="chat-input-bar">
          <textarea
            className="chat-textarea"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={cfg.inputPlaceholder || "Type your question here..."}
          />
          <button
            className="send-button"
            onClick={() => {
              if (input.trim()) {
                sendToChat(input);
                setInput("");
              }
            }}
            disabled={streaming || isThinking}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              width="24"
              height="24"
            >
              <path
                fill={streaming ? "#d7d7d7" : "#ffffff"}
                d="M22,11.7V12h-0.1c-0.1,1-17.7,9.5-18.8,9.1c-1.1-0.4,2.4-6.7,3-7.5C6.8,12.9,17.1,12,17.1,12H17c0,0,0-0.2,0-0.2c0,0,0,0,0,0c0-0.4-10.2-1-10.8-1.7c-0.6-0.7-4-7.1-3-7.5C4.3,2.1,22,10.5,22,11.7z"
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
