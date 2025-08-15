// src/utils/analytics.js

/**
 * Centralized analytics utility for Apollo Tyre AI Widget
 * Usage: import { trackEvent } from "../utils/analytics";
 */

export function trackEvent(eventName, data = {}) {
  // Example: send to backend or analytics provider
  // Replace with your actual tracking implementation
  if (window.sendAnalyticsEvent) {
    window.sendAnalyticsEvent(eventName, data);
  } else {
    // Fallback: log to console for development
    console.log(`[Analytics] ${eventName}`, data);
  }
}
