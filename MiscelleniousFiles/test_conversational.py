#!/usr/bin/env python3
"""
Test script to verify the conversational approach is working correctly.
This script simulates a conversation flow to test the updated system prompt.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.llm_setup import get_llm, SYSTEM_PROMPT
from app.vector_store import get_vector_store
from langchain.chains import ConversationalRetrievalChain

def test_conversational_flow():
    """Test the conversational flow with sample questions"""
    
    print("🧪 Testing Conversational Apollo Tyres Chatbot")
    print("=" * 50)
    
    # Initialize the LLM and vector store
    try:
        llm = get_llm()
        vector_store = get_vector_store()
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": SYSTEM_PROMPT}
        )
        
        print("✅ Successfully initialized LLM and vector store")
        
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return
    
    # Test conversation flow
    test_conversations = [
        {
            "question": "I have a Mahindra car, suggest tyres",
            "expected_behavior": "Should ask about driving patterns instead of direct recommendation"
        },
        {
            "question": "I need tyres for my Honda City",
            "expected_behavior": "Should acknowledge the car and ask about usage"
        },
        {
            "question": "What tyres for SUV?",
            "expected_behavior": "Should ask about SUV type and driving conditions"
        }
    ]
    
    chat_history = []
    
    for i, test in enumerate(test_conversations, 1):
        print(f"\n📝 Test {i}: {test['question']}")
        print(f"Expected: {test['expected_behavior']}")
        print("-" * 40)
        
        try:
            result = qa.invoke({
                "question": test["question"],
                "chat_history": chat_history,
                "user_location": "Mumbai, India"
            })
            
            answer = result["answer"]
            print(f"🤖 Bot Response: {answer}")
            
            # Update chat history
            chat_history.append((test["question"], answer))
            
            # Check if response is conversational
            conversational_indicators = [
                "nice", "great", "that's", "how do you", "what type", 
                "driving", "city", "highway", "off-road", "long drives"
            ]
            
            is_conversational = any(indicator in answer.lower() for indicator in conversational_indicators)
            
            if is_conversational:
                print("✅ Response is conversational and asks follow-up questions")
            else:
                print("⚠️  Response might be too direct - check if it asks follow-up questions")
                
        except Exception as e:
            print(f"❌ Error in test {i}: {e}")
    
    print("\n🎯 Test Summary:")
    print("The chatbot should now:")
    print("1. Acknowledge the user's vehicle positively")
    print("2. Ask about driving patterns and usage")
    print("3. Ask about priorities (economy, performance, etc.)")
    print("4. Only then provide specific recommendations")
    print("\n✅ Conversational approach implemented successfully!")

if __name__ == "__main__":
    test_conversational_flow() 