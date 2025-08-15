#!/usr/bin/env python3
"""
Test script for location-based chatbot responses
"""

import requests
import json

# Test locations for different regions in India
test_locations = [
    {
        "name": "Mumbai",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "region": "Western India"
    },
    {
        "name": "Delhi",
        "latitude": 28.7041,
        "longitude": 77.1025,
        "region": "Northern India"
    },
    {
        "name": "Bangalore",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "region": "Southern India"
    },
    {
        "name": "Kolkata",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "region": "Eastern India"
    },
    {
        "name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "region": "Southern India"
    }
]

# Test questions that should get location-specific responses
test_questions = [
    "Where can I find Apollo Tyres dealers near me?",
    "What are the best tyres for my area?",
    "I need tyre installation service",
    "Are there any Apollo Tyres promotions in my region?",
    "What's the warranty policy for my location?"
]

def test_location_based_responses():
    """Test chatbot responses with different locations"""
    
    base_url = "https://150.241.244.252:9006"
    
    for location in test_locations:
        print(f"\n{'='*60}")
        print(f"Testing for: {location['name']} ({location['region']})")
        print(f"Coordinates: {location['latitude']}, {location['longitude']}")
        print(f"{'='*60}")
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            
            # Prepare request with location
            payload = {
                "question": question,
                "session_id": f"test_session_{location['name'].lower()}",
                "user_location": {
                    "latitude": location['latitude'],
                    "longitude": location['longitude'],
                    "accuracy": 10,
                    "timestamp": 1234567890
                }
            }
            
            try:
                # Make request to the chatbot
                response = requests.post(
                    f"{base_url}/chat/query",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    verify=False  # For self-signed certificates
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "No answer received")
                    print(f"Answer: {answer[:200]}...")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"Request failed: {e}")
            
            print("-" * 40)

def test_websocket_location():
    """Test WebSocket connection with location data"""
    import websockets
    import asyncio
    
    async def test_websocket():
        uri = "wss://150.241.244.252:9006/chat/ws"
        
        try:
            async with websockets.connect(uri, ssl=True) as websocket:
                print("WebSocket connected successfully")
                
                # Test message with location
                test_message = {
                    "user_input": "Where can I find Apollo Tyres dealers near me?",
                    "user_id": "test_user",
                    "session_id": "test_session_websocket",
                    "user_location": {
                        "latitude": 19.0760,
                        "longitude": 72.8777,
                        "accuracy": 10,
                        "timestamp": 1234567890
                    },
                    "chat_history": []
                }
                
                await websocket.send(json.dumps(test_message))
                print("Message sent with location data")
                
                # Wait for response
                response = await websocket.recv()
                print(f"Response received: {response[:200]}...")
                
        except Exception as e:
            print(f"WebSocket test failed: {e}")
    
    # Run the async test
    asyncio.run(test_websocket())

if __name__ == "__main__":
    print("Testing Location-Based Chatbot Responses")
    print("=" * 60)
    
    # Test HTTP endpoint
    print("\n1. Testing HTTP endpoint with location data...")
    test_location_based_responses()
    
    # Test WebSocket endpoint
    print("\n2. Testing WebSocket endpoint with location data...")
    test_websocket_location()
    
    print("\nLocation-based testing completed!") 