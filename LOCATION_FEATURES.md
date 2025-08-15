# Location-Based Chatbot Features

## Overview

The Apollo Tyres chatbot now supports location-based responses, allowing it to provide region-specific information, dealer recommendations, and localized services based on the user's geographic location.

## How It Works

### 1. **Location Detection**
- Automatically detects user's location when the page loads
- Uses browser's Geolocation API with fallback handling
- Stores location data in localStorage for session persistence

### 2. **Location-Based Session IDs**
- Creates session IDs that include geographic coordinates
- Format: `session_{latitude}_{longitude}_{timestamp}`
- Helps track users by location for analytics

### 3. **Regional Context Recognition**
The system recognizes different regions in India:

#### **Major Regions:**
- **Western India** (Maharashtra, Gujarat): 20°N-30°N, 70°E-80°E
- **Southern India** (Karnataka, Kerala, Tamil Nadu): 10°N-20°N, 70°E-80°E
- **Central India** (Madhya Pradesh, Chhattisgarh): 20°N-30°N, 80°E-90°E
- **Eastern India** (West Bengal, Odisha): 20°N-30°N, 90°E-100°E
- **Northern India** (Punjab, Haryana, Delhi): 30°N-37°N, 70°E-80°E

#### **Specific Cities:**
- **Mumbai**: 19.0760°N, 72.8777°E
- **Delhi**: 28.7041°N, 77.1025°E
- **Bangalore**: 12.9716°N, 77.5946°E
- **Chennai**: 13.0827°N, 80.2707°E
- **Kolkata**: 22.5726°N, 88.3639°E

### 4. **Location-Specific Responses**

The chatbot can now provide:

#### **Dealer Information**
- "I can help you find Apollo Tyres dealers in your area. Based on your location in Western India, there are several authorized dealers in Maharashtra and Gujarat..."

#### **Regional Promotions**
- "Great news! Apollo Tyres is currently running special promotions in your region. In Southern India, we have exclusive offers on SUV tyres..."

#### **Weather-Based Recommendations**
- "Given your location in Northern India, I'd recommend our all-weather tyres that perform well in both hot summers and cold winters..."

#### **Local Service Centers**
- "For tyre installation and service, I recommend visiting our authorized service centers in your area. In Bangalore, we have multiple locations..."

#### **Regional Warranty Information**
- "Apollo Tyres warranty policies are consistent across India, but service centers and claim processing may vary by region..."

## Technical Implementation

### Frontend Changes
- **Location Detection**: Automatic geolocation with user consent
- **Session Management**: Location-based session IDs
- **Data Transmission**: Location data sent with each message
- **Visual Indicators**: Location display in chatbot header

### Backend Changes
- **LLM Integration**: Location context passed to AI model
- **Regional Mapping**: Coordinate-based region identification
- **Database Storage**: Location data stored in sessions table
- **Analytics**: Location tracking for user behavior analysis

### API Endpoints
- **HTTP POST** `/chat/query` - Supports location in request body
- **WebSocket** `/chat/ws` - Real-time location-aware chat

## Example Usage

### HTTP Request
```json
{
  "question": "Where can I find Apollo Tyres dealers near me?",
  "session_id": "session_19.0760_72.8777_1234567890",
  "user_location": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "accuracy": 10,
    "timestamp": 1234567890
  }
}
```

### WebSocket Message
```json
{
  "user_input": "I need tyre installation service",
  "user_id": "user_123",
  "session_id": "session_19.0760_72.8777_1234567890",
  "user_location": {
    "latitude": 19.0760,
    "longitude": 72.8777,
    "accuracy": 10,
    "timestamp": 1234567890
  },
  "chat_history": []
}
```

## Privacy & Security

### **Data Protection**
- Coordinates rounded to 4 decimal places for privacy
- Location data only used for service recommendations
- No precise location tracking or storage

### **User Consent**
- Browser prompts for location permission
- Graceful fallback when location access denied
- Clear indication when location is being used

### **Session Cleanup**
- Location data cleared when session ends
- Automatic cleanup on page unload
- No persistent location storage

## Testing

### Manual Testing
1. Open the chatbot in different locations
2. Ask location-specific questions
3. Verify regional responses
4. Test with location access denied

### Automated Testing
Run the test script:
```bash
python test-location-chat.py
```

This will test responses for different Indian cities and regions.

## Benefits

1. **Personalized Experience**: Users get relevant local information
2. **Better Recommendations**: Location-aware tyre suggestions
3. **Improved Customer Service**: Regional dealer and service information
4. **Enhanced Analytics**: Location-based user behavior tracking
5. **Competitive Advantage**: Location-aware AI assistant

## Future Enhancements

- **Real-time Weather Integration**: Weather-based tyre recommendations
- **Local Event Integration**: Regional promotions and events
- **Dealer API Integration**: Real-time dealer availability
- **Multi-language Support**: Regional language preferences
- **Traffic Integration**: Route-based tyre recommendations 