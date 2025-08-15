// src/config.js
const config = {
  companyName: "Sobha Ltd.",
  companyLogo: "https://realtyseek.ai/demo/sobha-altus/images/sobha-logo.png", // Replace with your logo URL or asset path
  agentName: "Sobha AI Agent",
  agentKey: "sobha",
  pageUrl:  "https://realtyseek.ai/demo/sobha-altus/index.html-test",
  projectName: "Sobha Altus",
  chatUrl: "wss://aryan.realtyseek.ai/ws/chat",
  phoneSubmitUrl: "https://aryan.realtyseek.ai/api/mobile",
  theme: {
    primaryColor: "#004aad",
    secondaryColor: "#f0f0f0",
    backgroundColor: "#ffffff",
    textColor: "#333333"
  },
  // Customizable introductory message
  introductionText: `
### 🏡 Welcome. Discover Sobha Altus
`,
suggestedQuestions: [
  "What 3, 4, and 5 BHK options are available at Sobha Altus?",
  "What is the price range for each apartment configuration?",
  "Is Sobha Altus a new launch or under construction?",
  "When is the expected completion date?",
  "What are the main amenities at Sobha Altus?",
  "What features does “The Waverly Club” offer?",
  "Does Sobha Altus have IGBC green‐home certification?",
  "How far is Sobha Altus from IGI Airport?",
  "Which schools and hospitals are nearby?",
  "What makes Sobha Altus a good investment?"
],
showNumberOfQuestions: 3,
inputPlaceholder: "Ask anything ..."
};

export default config;

