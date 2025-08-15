// src/config.js
const config = {
  companyName: "Aryan Realty",
  companyLogo: "https://realtyseek.ai/images/aryan-logo.webp", // Replace with your logo URL or asset path
  agentName: "Aryan AI Agent",
  agentKey: "aryan",
  //pageUrl:  "https://daxinvistas.signatureglobalproject.com",
  projectName: "Aryan Projects",
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
### 🏡 Welcome to Aryan Realty !!!`,
showNumberOfQuestions: 3,
inputPlaceholder: "Ask anything ..."
};

export default config;

