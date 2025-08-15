#!/usr/bin/env python3
"""
Test script for inactive user marking functionality
"""

import requests
import json
import time

def test_inactive_users():
    """Test the inactive user marking functionality"""
    
    base_url = "https://150.241.244.252:9006"
    
    print("Testing inactive user marking functionality...")
    print("=" * 60)
    
    # Test 1: Check current active users
    try:
        response = requests.get(f"{base_url}/analytics/", verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"Current total users: {data.get('total_users', 0)}")
            
            # Check active users in database
            active_users = requests.get(f"{base_url}/analytics/sessions", verify=False)
            if active_users.status_code == 200:
                active_data = active_users.json()
                print(f"Active sessions: {active_data.get('active_sessions', 0)}")
        else:
            print(f"Error getting analytics: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Manually trigger inactive user marking
    try:
        print("\nTriggering inactive user marking...")
        response = requests.post(f"{base_url}/analytics/mark_inactive", verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('message', 'Users marked as inactive')}")
        else:
            print(f"Error marking inactive users: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Check again after marking
    try:
        print("\nChecking status after marking inactive users...")
        response = requests.get(f"{base_url}/analytics/", verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"Total users after marking: {data.get('total_users', 0)}")
            
            # Check active sessions
            active_users = requests.get(f"{base_url}/analytics/sessions", verify=False)
            if active_users.status_code == 200:
                active_data = active_users.json()
                print(f"Active sessions after marking: {active_data.get('active_sessions', 0)}")
        else:
            print(f"Error getting analytics: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_inactive_users() 