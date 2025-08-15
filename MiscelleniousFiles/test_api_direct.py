#!/usr/bin/env python3
"""
Direct API test for Apollo Tyres chatbot
Tests the conversational approach through the actual API endpoints
"""

import requests
import json
import time

def test_chatbot_api():
    """Test the chatbot API directly"""
    
    print("🧪 Testing Apollo Tyres Chatbot API - Direct Testing")
    print("=" * 60)
    
    # API endpoint
    base_url = "http://localhost:9006"
    
    # Test questions based on the conversational approach
    test_questions = [
        {
            "question": "I have a Honda City, suggest tyres",
            "expected_keywords": ["honda", "city", "comfort", "alnac", "amazer", "driving"],
            "expected_behavior": "Should acknowledge Honda City and ask about driving patterns"
        },
        {
            "question": "I need tyres for my Mahindra XUV500",
            "expected_keywords": ["mahindra", "xuv", "apterra", "durability", "driving"],
            "expected_behavior": "Should mention Apterra range and ask about usage"
        },
        {
            "question": "I want affordable tyres for my Maruti Swift",
            "expected_keywords": ["maruti", "swift", "affordable", "budget", "driving"],
            "expected_behavior": "Should acknowledge budget concern and ask about priorities"
        },
        {
            "question": "What is the warranty on Apollo tyres?",
            "expected_keywords": ["warranty", "5-year", "3-year", "manufacturing"],
            "expected_behavior": "Should provide warranty information directly"
        }
    ]
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {test['question']}")
        print(f"Expected: {test['expected_behavior']}")
        print("-" * 50)
        
        try:
            # Test the query endpoint
            response = requests.post(
                f"{base_url}/chat/query",
                json={
                    "question": test["question"],
                    "session_id": f"test_session_{i}",
                    "user_location": {"latitude": 19.0760, "longitude": 72.8777}  # Mumbai
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "")
                print(f"🤖 Bot Response: {answer}")
                
                # Check for expected keywords
                answer_lower = answer.lower()
                found_keywords = []
                missing_keywords = []
                
                for keyword in test["expected_keywords"]:
                    if keyword.lower() in answer_lower:
                        found_keywords.append(keyword)
                    else:
                        missing_keywords.append(keyword)
                
                # Check conversational indicators
                conversational_indicators = [
                    "that's", "great", "nice", "perfect", "got it", "based on",
                    "many", "drivers", "owners", "prefer", "excellent", "choice"
                ]
                
                is_conversational = any(indicator in answer_lower for indicator in conversational_indicators)
                
                # Check if it asks follow-up questions
                question_indicators = [
                    "do you", "can i ask", "would you", "are you", "how do you",
                    "what type", "mostly", "usually", "focused on"
                ]
                
                asks_questions = any(indicator in answer_lower for indicator in question_indicators)
                
                # Evaluation
                print(f"\n📊 Evaluation:")
                print(f"✅ Found keywords: {found_keywords}")
                if missing_keywords:
                    print(f"⚠️  Missing keywords: {missing_keywords}")
                
                if is_conversational:
                    print("✅ Response is conversational and friendly")
                else:
                    print("⚠️  Response might be too formal")
                    
                if asks_questions:
                    print("✅ Asks follow-up questions appropriately")
                else:
                    print("⚠️  Doesn't ask follow-up questions")
                    
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network Error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Small delay between requests
    
    print("\n🎯 Test Summary:")
    print("The chatbot should demonstrate:")
    print("1. ✅ Acknowledges vehicles positively")
    print("2. ✅ Suggests initial Apollo options")
    print("3. ✅ Asks relevant follow-up questions")
    print("4. ✅ Maintains conversational tone")
    print("5. ✅ Provides helpful, specific information")

def test_websocket_connection():
    """Test WebSocket connection"""
    print("\n🔌 Testing WebSocket Connection")
    print("=" * 40)
    
    try:
        import websocket
        import json
        
        # Test WebSocket connection
        ws = websocket.create_connection("ws://localhost:9006/chat/ws", timeout=10)
        
        # Send a test message
        test_message = {
            "user_input": "I have a Honda City, suggest tyres",
            "user_location": {"latitude": 19.0760, "longitude": 72.8777},
            "page_url": "https://apollotyres.com"
        }
        
        ws.send(json.dumps(test_message))
        
        # Wait for response
        response = ws.recv()
        response_data = json.loads(response)
        
        print(f"🤖 WebSocket Response: {response_data.get('text', 'No text in response')}")
        
        ws.close()
        print("✅ WebSocket test completed")
        
    except ImportError:
        print("⚠️  websocket-client not installed, skipping WebSocket test")
    except Exception as e:
        print(f"❌ WebSocket Error: {e}")

if __name__ == "__main__":
    test_chatbot_api()
    test_websocket_connection() 