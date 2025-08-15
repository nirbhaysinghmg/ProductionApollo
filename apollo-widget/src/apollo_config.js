// src/config.js
const config = {
  companyName: "Apollo Tyres",
  companyLogo: "https://realtyseek.ai/images/apollo_tyres_logo.png", // Replace with your logo URL or asset path
  agentName: "Apollo Tyres AI Assistant",
  agentKey: "apollo",
  //pageUrl:  "https://daxinvistas.signatureglobalproject.com",
  projectName: "Apollo Tyres Details",
  chatUrl: "wss://150.241.244.252:9006/ws/chat",
//  chatUrl: "wss://apollo.realtyseek.ai/ws/chat",
  phoneSubmitUrl: "https://apollo.realtyseek.ai/api/mobile",
  theme: {
    primaryColor: "#004aad",
    secondaryColor: "#f0f0f0",
    backgroundColor: "#ffffff",
    textColor: "#333333"
  },
  // Customizable introductory message
  introductionText: `
### 🏡 Welcome to Apollo Tyres !!!`,
showNumberOfQuestions: 0,
collectMobileAfterNumberOfQuestion: 10,
inputPlaceholder: "Ask anything about Apollo Tyres ..."
};

export default config;

