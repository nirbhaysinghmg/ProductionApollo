# Conversational Apollo Tyres Chatbot

## Overview

The Apollo Tyres chatbot has been updated to provide a more conversational and interactive experience. Instead of immediately providing tyre recommendations, the chatbot now engages users in a dialogue to understand their specific needs and preferences.

## Conversational Flow

### 1. Vehicle Acknowledgment
When a user mentions their vehicle, the chatbot responds positively:
- **User**: "I have a Mahindra car, suggest tyres"
- **Bot**: "That's a nice car you have there! How do you drive? Long drives, off-roading, or city drive?"

### 2. Driving Pattern Questions
The chatbot asks about usage patterns:
- City driving vs highway driving
- Long trips vs short commutes
- Off-roading vs regular roads
- Load carrying requirements

### 3. Priority Assessment
Based on driving patterns, the chatbot asks about priorities:
- Fuel efficiency vs performance
- Comfort vs durability
- Budget considerations
- Weather and road conditions

### 4. Specific Recommendations
Only after gathering sufficient information, the chatbot provides personalized tyre recommendations with reasoning.

## Example Conversation Flow

```
User: "I have a Mahindra car, suggest tyres"
Bot: "That's a nice car you have there! How do you drive? Long drives, off-roading, or city drive?"

User: "Mostly city driving"
Bot: "Great! Since you drive mostly in the city, economy and comfort are important. Do you prioritize fuel efficiency, or are you looking for better performance and handling?"

User: "Fuel efficiency is important"
Bot: "Perfect! For city driving with fuel efficiency in mind, I'd recommend Apollo's Amazer 4G Life tyres. They're designed specifically for fuel economy and smooth city driving..."
```

## Key Features

### Conversational Indicators
The chatbot uses friendly, conversational language:
- "That's a nice car you have there!"
- "Great! Since you drive mostly in the city..."
- "Perfect! For city driving with fuel efficiency in mind..."

### Information Gathering
The chatbot systematically gathers:
1. **Vehicle Information**: Make, model, year
2. **Driving Patterns**: Usage type, frequency, distance
3. **Priorities**: Performance, economy, comfort, budget
4. **Conditions**: Weather, road conditions, load
5. **Experience**: Driver experience level

### Personalized Recommendations
Based on gathered information, the chatbot provides:
- Specific Apollo Tyres product recommendations
- Reasoning for the recommendations
- Location-specific dealer information
- Warranty and service details

## Technical Implementation

### Updated System Prompt
The system prompt in `app/llm_setup.py` has been updated to:
- Encourage conversational responses
- Ask follow-up questions before recommendations
- Gather comprehensive user information
- Provide personalized advice

### Suggested Questions
The suggested questions generation has been updated to focus on user questions about:
- Specific Apollo tyre models and their features
- Warranty information and coverage
- Pricing and budget options
- Performance features and benefits
- Dealer locations and services
- Tyre maintenance and care
- Installation and fitting services
- Product comparisons and recommendations

## Benefits

1. **Better User Experience**: More engaging and natural conversation
2. **Accurate Recommendations**: Based on comprehensive user information
3. **Higher Satisfaction**: Users feel heard and understood
4. **Increased Sales**: More targeted product recommendations
5. **Reduced Returns**: Better matching of products to user needs

## Testing

Use the `test_conversational.py` script to verify the conversational approach:

```bash
python test_conversational.py
```

This will test various conversation scenarios and verify that the chatbot:
- Acknowledges vehicles positively
- Asks appropriate follow-up questions
- Provides personalized recommendations
- Maintains conversational tone

## Maintenance

The conversational approach is implemented through:
- **System Prompt**: `app/llm_setup.py`
- **Question Generation**: `app/routers/chat.py`
- **Vector Store**: `app/vector_store.py`
- **Analytics**: `app/analytics.py`

All components work together to provide a seamless conversational experience. 