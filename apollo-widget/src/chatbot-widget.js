// src/chatbot-widget.js

import React from 'react';
import ReactDOM from 'react-dom';
import ChatWidget from './components/ChatWidget';
import './components/ChatWidget.css';  // Widget styles

// UMD export: exposes ChatBotWidget.init(...)
const ChatBotWidget = {
  init: (userConfig) => {
    // Allow passing either a selector string or a DOM node
    const container =
      typeof userConfig.container === 'string'
        ? document.querySelector(userConfig.container)
        : userConfig.container;

    if (!container) {
      console.error(`Chatbot container not found: ${userConfig.container}`);
      return;
    }

    // Render the React ChatWidget, spreading all userConfig entries as props
    ReactDOM.render(
      <ChatWidget {...userConfig} />,
      container
    );
  }
};

export default ChatBotWidget;
