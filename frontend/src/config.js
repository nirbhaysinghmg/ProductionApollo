// src/config.js
const config = {
  companyName: "Apollo Tyres",
  companyLogo: "assets/images/apollo_logo.png",
  agentName: "Apollo AI Agent",
  projectName: "Apollo Tyres AI bot",
  chatUrl:
    window.location.protocol === "https:" || window.location.protocol === "wss:"
      ? "wss://150.241.244.252:9006/chat/ws"
      : "ws://150.241.244.252:9006/chat/ws", // WebSocket endpoint in chat router
  phoneSubmitUrl:
    window.location.protocol === "https:"
      ? "https://150.241.244.252:9006/api/mobile"
      : "http://150.241.244.252:9006/api/mobile",
  theme: {
    primaryColor: "#0066cc",
    secondaryColor: "#f0f0f0",
    backgroundColor: "#ffffff",
    textColor: "#333333",
  },
  // Customizable introductory message
  introductionText: `
### 👋 Welcome to our AI Help Chat.
  `,
  // Initial hardcoded suggested questions (first 5)
  initialSuggestedQuestions: [
    "What is the warranty period for Apollo tyres?",
    "How do I claim warranty for my tyres?",
    "What is covered under tyre warranty?",
    "How to check warranty status of my tyres?",
    "What documents are needed for warranty claim?",
  ],
  // Number of questions to show at a time (default: 3)
  showNumberOfQuestions: 3,
  inputPlaceholder: "Type your question here...",
  // API endpoint for generating dynamic questions
  dynamicQuestionsUrl:
    window.location.protocol === "https:"
      ? "https://150.241.244.252:9006/chat/generate-questions"
      : "http://150.241.244.252:9006/chat/generate-questions",
};

export default config;
