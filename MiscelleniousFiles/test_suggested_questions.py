#!/usr/bin/env python3
"""
Test script to verify suggested questions are from user's perspective
"""

import requests
import json

def test_suggested_questions():
    """Test that suggested questions are user-focused, not chatbot questions"""
    
    print("🧪 Testing Suggested Questions - User Perspective")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        {
            "conversation_history": [
                {"role": "user", "content": "I have a Honda City, suggest tyres"},
                {"role": "assistant", "content": "That's a great vehicle — many Honda City owners prefer Apollo's Alnac 4G or Amazer 4G Life for comfort and smooth rides. But before we lock it in, can I ask — do you mostly drive within the city, go on long drives, or do some off-roading too?"}
            ],
            "current_topic": "Honda City tyre recommendations",
            "expected_user_questions": [
                "warranty", "dealer", "price", "maintenance", "specifications"
            ]
        },
        {
            "conversation_history": [
                {"role": "user", "content": "What is the warranty on Apollo tyres?"},
                {"role": "assistant", "content": "Apollo Tyres offers a 5-year manufacturing warranty for passenger car tyres and 3-year warranty for commercial vehicle tyres from the date of purchase."}
            ],
            "current_topic": "Apollo tyres warranty",
            "expected_user_questions": [
                "warranty", "coverage", "claim", "defects", "receipt"
            ]
        }
    ]
    
    base_url = "http://localhost:9006"
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Test {i}: {scenario['current_topic']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/chat/generate-questions",
                json={
                    "conversation_history": scenario["conversation_history"],
                    "current_topic": scenario["current_topic"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                questions = result.get("questions", [])
                
                print(f"🤖 Generated Questions:")
                for j, question in enumerate(questions, 1):
                    print(f"  {j}. {question}")
                
                # Check if questions are user-focused (not chatbot questions)
                user_focused_indicators = [
                    "what is", "how do", "where can", "what are", "how to",
                    "warranty", "dealer", "price", "maintenance", "specifications",
                    "installation", "service", "coverage", "claim"
                ]
                
                chatbot_question_indicators = [
                    "do you", "can i ask", "would you", "are you", "how do you",
                    "what type", "mostly", "usually", "focused on", "driving"
                ]
                
                user_focused_count = 0
                chatbot_question_count = 0
                
                for question in questions:
                    question_lower = question.lower()
                    
                    # Check for user-focused questions
                    if any(indicator in question_lower for indicator in user_focused_indicators):
                        user_focused_count += 1
                    
                    # Check for chatbot questions (should be avoided)
                    if any(indicator in question_lower for indicator in chatbot_question_indicators):
                        chatbot_question_count += 1
                
                print(f"\n📊 Evaluation:")
                print(f"✅ User-focused questions: {user_focused_count}/{len(questions)}")
                print(f"⚠️  Chatbot-style questions: {chatbot_question_count}/{len(questions)}")
                
                if user_focused_count > chatbot_question_count:
                    print("✅ Questions are correctly user-focused")
                else:
                    print("⚠️  Questions might be too chatbot-focused")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎯 Summary:")
    print("Suggested questions should be:")
    print("✅ From user's perspective (what users would ask)")
    print("✅ About Apollo Tyres products and services")
    print("✅ Natural and conversational")
    print("❌ NOT questions the chatbot asks to users")

if __name__ == "__main__":
    test_suggested_questions() 