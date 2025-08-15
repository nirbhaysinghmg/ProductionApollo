# Manual Test Questions for Apollo Tyres Chatbot

## 🎯 Quick Test Questions

Use these questions to manually test if the chatbot is working correctly with the conversational approach:

### 🚗 Vehicle-Specific Questions
1. **"I have a Honda City, suggest tyres"**
   - ✅ Should acknowledge Honda City positively
   - ✅ Should suggest initial Apollo options (Alnac 4G, Amazer 4G Life)
   - ✅ Should ask about driving patterns (city/highway/off-road)

2. **"I need tyres for my Mahindra XUV500"**
   - ✅ Should mention Apterra range for durability
   - ✅ Should ask about usage patterns
   - ✅ Should be conversational and friendly

3. **"Suggest tyres for my Royal Enfield"**
   - ✅ Should acknowledge the bike
   - ✅ Should ask about riding patterns
   - ✅ Should suggest appropriate two-wheeler options

### 💰 Budget & Priority Questions
4. **"I want affordable tyres for my Maruti Swift"**
   - ✅ Should acknowledge budget concern
   - ✅ Should ask about priorities and usage
   - ✅ Should suggest economical options

5. **"I want high-performance tyres for my sports car"**
   - ✅ Should focus on performance aspects
   - ✅ Should ask about usage (track/highway)
   - ✅ Should suggest performance-oriented options

### 🌦️ Weather & Condition Questions
6. **"I need tyres for monsoon season"**
   - ✅ Should ask about vehicle type
   - ✅ Should focus on wet grip and safety
   - ✅ Should suggest weather-appropriate options

7. **"I do off-roading, suggest tyres"**
   - ✅ Should ask about vehicle type
   - ✅ Should focus on terrain and durability
   - ✅ Should suggest all-terrain options

### 🛣️ Usage Pattern Questions
8. **"I do a lot of highway driving, suggest tyres"**
   - ✅ Should ask about vehicle type
   - ✅ Should focus on comfort and durability
   - ✅ Should suggest highway-appropriate options

9. **"I only drive in the city, what tyres should I get?"**
   - ✅ Should ask about vehicle type
   - ✅ Should focus on fuel efficiency and comfort
   - ✅ Should suggest city-appropriate options

### 🔧 Technical Questions
10. **"What is the warranty on Apollo tyres?"**
    - ✅ Should provide warranty information directly
    - ✅ Should mention 5-year for passenger cars
    - ✅ Should mention 3-year for commercial vehicles

11. **"I need 205/55R16 tyres for my car"**
    - ✅ Should acknowledge the size specification
    - ✅ Should ask about vehicle type and usage
    - ✅ Should suggest appropriate options for that size

### 📍 Location Questions
12. **"I'm in Mumbai, where can I find Apollo dealers?"**
    - ✅ Should provide location-specific information
    - ✅ Should mention authorized dealers
    - ✅ Should be helpful and specific

### ⛽ Feature-Specific Questions
13. **"I want fuel-efficient tyres"**
    - ✅ Should ask about vehicle type
    - ✅ Should ask about driving patterns
    - ✅ Should suggest fuel-efficient options

14. **"I want quiet tyres for a comfortable ride"**
    - ✅ Should ask about vehicle type
    - ✅ Should focus on comfort and noise reduction
    - ✅ Should suggest quiet ride options

## 🎭 Expected Conversational Indicators

The chatbot should use friendly, conversational language like:
- ✅ "That's a great vehicle..."
- ✅ "Many drivers prefer..."
- ✅ "Based on that..."
- ✅ "Perfect! For [usage]..."
- ✅ "Got it! For [condition]..."

## ❓ Expected Follow-up Questions

The chatbot should ask questions like:
- ✅ "Do you mostly drive in the city, go on long drives, or do some off-roading?"
- ✅ "Would you say you're more focused on saving fuel, or do you enjoy performance?"
- ✅ "Can I ask about your driving patterns?"
- ✅ "What type of vehicle do you have?"

## 🚫 What to Avoid

The chatbot should NOT:
- ❌ Give direct recommendations without asking questions
- ❌ Sound robotic or overly formal
- ❌ Ignore the conversational approach
- ❌ Provide generic answers without personalization

## 🔄 Complete Conversation Test

Test this complete flow:

**User**: "I have a Mahindra XUV500, suggest tyres"
**Expected Bot**: "That's a great vehicle — many Mahindra owners prefer Apollo's Apterra range for its durability and all-terrain handling. But before we lock it in, can I ask — do you mostly drive within the city, go on long drives, or do some off-roading too?"

**User**: "Mostly city driving"
**Expected Bot**: "Got it! For smooth city drives, comfort and fuel efficiency matter most. Would you say you're more focused on saving fuel, or do you enjoy performance and a quiet ride too?"

**User**: "Fuel efficiency is important"
**Expected Bot**: "Perfect. Based on that, Apollo's Amazer 4G Life is an excellent choice — it's built for great mileage and long tread life in urban conditions..."

## 📊 Evaluation Checklist

For each test question, verify:
- [ ] Bot acknowledges the vehicle/requirement positively
- [ ] Bot suggests initial Apollo options
- [ ] Bot asks relevant follow-up questions
- [ ] Bot maintains conversational tone
- [ ] Bot provides helpful, specific information
- [ ] Bot doesn't sound robotic or overly formal 