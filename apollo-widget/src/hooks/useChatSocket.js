// src/hooks/useChatSocket.js
import { useRef, useEffect, useCallback } from 'react';
import config from '../apollo_config';

const chatUrl = config.chatUrl;
const MAX_RETRIES = 5;

export const useChatSocket = (setChatHistory, setStreaming, setIsThinking) => {
  const ws = useRef(null);
  const retryCount = useRef(0);
  const reconnectTimeout = useRef(null);

  const waitForConnection = useCallback((timeout = 5000, interval = 500) => {
    return new Promise((resolve, reject) => {
      const start = Date.now();
      const check = () => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          resolve();
        } else if (Date.now() - start > timeout) {
          reject(new Error("Timeout waiting for WebSocket connection."));
        } else {
          setTimeout(check, interval);
        }
      };
      check();
    });
  }, []);

  const connectWebSocket = useCallback(() => {
    console.log("Connecting WebSocket… retry", retryCount.current);
    ws.current = new WebSocket(chatUrl);

    ws.current.onopen = () => {
      console.log("WebSocket open");
      retryCount.current = 0;
    };

    ws.current.onmessage = (evt) => {
      let data;
      try {
        data = JSON.parse(evt.data);
      } catch (err) {
        console.error("Bad JSON:", err);
        return;
      }

      if (data.error) {
        setChatHistory(prev => [...prev, { role: "error", text: data.error }]);
        setStreaming(false);
        setIsThinking(false);
      }

      if (data.chunk) {
        // hide "thinking" as soon as the first chunk arrives
        setIsThinking(false);

        setChatHistory(prev => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && !last.completed) {
            return [
              ...prev.slice(0, -1),
              { ...last, text: last.text + data.chunk }
            ];
          }
          return [...prev, { role: "assistant", text: data.chunk, completed: false }];
        });
        // NOTE: we do NOT setStreaming(false) here so streaming continues until data.end
      }

      if (data.end) {
        setChatHistory(prev => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") {
            return [
              ...prev.slice(0, -1),
              { ...last, completed: true }
            ];
          }
          return prev;
        });
        setStreaming(false);
        setIsThinking(false);
      }
    };

    ws.current.onerror = (err) => {
      console.error("WebSocket error:", err);
      setStreaming(false);
      setIsThinking(false);
      ws.current.close();
    };

    ws.current.onclose = (evt) => {
      console.log("WebSocket closed:", evt.code, evt.reason);
      if (retryCount.current < MAX_RETRIES) {
        const delay = Math.min(1000 * 2 ** retryCount.current, 30000);
        reconnectTimeout.current = setTimeout(() => {
          retryCount.current += 1;
          connectWebSocket();
        }, delay);
      } else {
        console.error("Max retries reached.");
      }
    };
  }, [setChatHistory, setStreaming, setIsThinking]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      clearTimeout(reconnectTimeout.current);
      retryCount.current = 0;
      ws.current?.close();
    };
  }, [connectWebSocket]);

  return { ws, waitForConnection };
};
