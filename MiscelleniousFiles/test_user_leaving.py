#!/usr/bin/env python3
"""
Test script for user leaving functionality
"""

import requests
import json
import time

def test_user_leaving():
    """Test the user leaving functionality"""
    
    base_url = "https://150.241.244.252:9006"
    
    print("Testing user leaving functionality...")
    print("=" * 60)
    
    # Test 1: Check current active users
    try:
        response = requests.get(f"{base_url}/analytics/", verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"Current total users: {data.get('total_users', 0)}")
            
            # Check active sessions
            active_users = requests.get(f"{base_url}/analytics/sessions", verify=False)
            if active_users.status_code == 200:
                active_data = active_users.json()
                print(f"Active sessions: {active_data.get('active_sessions', 0)}")
        else:
            print(f"Error getting analytics: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Simulate user leaving
    try:
        print("\nSimulating user leaving...")
        test_data = {
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "reason": "page_closed",
            "timestamp": "2024-01-01T12:00:00"
        }
        
        response = requests.post(f"{base_url}/analytics/user_left", 
                               json=test_data, verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('message', 'User left event recorded')}")
        else:
            print(f"Error recording user left: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Trigger timeout cleanup
    try:
        print("\nTriggering timeout cleanup...")
        response = requests.post(f"{base_url}/analytics/mark_inactive_timeout", verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('message', 'Users marked as inactive')}")
        else:
            print(f"Error marking inactive users: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Check status after cleanup
    try:
        print("\nChecking status after cleanup...")
        response = requests.get(f"{base_url}/analytics/", verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"Total users after cleanup: {data.get('total_users', 0)}")
            
            # Check active sessions
            active_users = requests.get(f"{base_url}/analytics/sessions", verify=False)
            if active_users.status_code == 200:
                active_data = active_users.json()
                print(f"Active sessions after cleanup: {active_data.get('active_sessions', 0)}")
        else:
            print(f"Error getting analytics: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_user_leaving() 