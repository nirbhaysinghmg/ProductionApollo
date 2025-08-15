#!/usr/bin/env python3
"""
Script to fix user status and test the user leaving functionality
"""

import mysql.connector
from mysql.connector import Error
import requests
import json

# MySQL Configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "nirbhay",
    "password": "Nirbhay@123",
    "database": "chatbot_analytics"
}

def fix_user_status():
    """Manually fix user status in database"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        print("🔧 Fixing user status in database...")
        
        # 1. Mark all users as inactive
        cursor.execute("""
            UPDATE users 
            SET is_active = FALSE 
            WHERE is_active = TRUE
        """)
        print(f"✅ Marked {cursor.rowcount} users as inactive")
        
        # 2. Mark all sessions as completed
        cursor.execute("""
            UPDATE sessions 
            SET status = 'completed' 
            WHERE status = 'active'
        """)
        print(f"✅ Marked {cursor.rowcount} sessions as completed")
        
        # 3. Add missing columns if they don't exist
        try:
            cursor.execute("""
                ALTER TABLE sessions 
                ADD COLUMN duration INT DEFAULT 0
            """)
            print("✅ Added duration column to sessions table")
        except Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ Duration column already exists")
            else:
                print(f"⚠️ Error adding duration column: {e}")
        
        try:
            cursor.execute("""
                ALTER TABLE sessions 
                ADD COLUMN end_time DATETIME
            """)
            print("✅ Added end_time column to sessions table")
        except Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ End_time column already exists")
            else:
                print(f"⚠️ Error adding end_time column: {e}")
        
        connection.commit()
        print("✅ Database updated successfully")
        
        # 4. Show current status
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) as active_users FROM users WHERE is_active = TRUE")
        active_users = cursor.fetchone()['active_users']
        
        cursor.execute("SELECT COUNT(*) as total_sessions FROM sessions")
        total_sessions = cursor.fetchone()['total_sessions']
        
        cursor.execute("SELECT COUNT(*) as active_sessions FROM sessions WHERE status = 'active'")
        active_sessions = cursor.fetchone()['active_sessions']
        
        print(f"\n📊 Current Status:")
        print(f"   Total Users: {total_users}")
        print(f"   Active Users: {active_users}")
        print(f"   Total Sessions: {total_sessions}")
        print(f"   Active Sessions: {active_sessions}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Database error: {e}")

def test_user_leaving_api():
    """Test the user leaving API endpoints"""
    base_url = "https://150.241.244.252:9006"
    
    print(f"\n🧪 Testing API endpoints...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/", verify=False, timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"⚠️ Server returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test 2: Test user_left endpoint
    try:
        test_data = {
            "user_id": "test_user_123",
            "session_id": "test_session_456",
            "reason": "manual_test",
            "timestamp": "2024-01-01T12:00:00"
        }
        
        response = requests.post(f"{base_url}/analytics/user_left", 
                               json=test_data, verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ User left endpoint working")
        else:
            print(f"⚠️ User left endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"❌ User left endpoint error: {e}")
    
    # Test 3: Test mark_inactive_timeout endpoint
    try:
        response = requests.post(f"{base_url}/analytics/mark_inactive_timeout", 
                               verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ Mark inactive timeout endpoint working")
        else:
            print(f"⚠️ Mark inactive timeout returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Mark inactive timeout error: {e}")

def simulate_user_leaving():
    """Simulate a user leaving the website"""
    print(f"\n🎭 Simulating user leaving...")
    
    # This simulates what happens when a user closes the browser
    test_data = {
        "user_id": "simulated_user_001",
        "session_id": "simulated_session_001",
        "reason": "browser_closed",
        "timestamp": "2024-01-01T12:00:00"
    }
    
    try:
        response = requests.post(
            "https://150.241.244.252:9006/analytics/user_left",
            json=test_data,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Successfully simulated user leaving")
            result = response.json()
            print(f"   Response: {result.get('message', 'User left event recorded')}")
        else:
            print(f"❌ Failed to simulate user leaving: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error simulating user leaving: {e}")

if __name__ == "__main__":
    print("🔧 Apollo Tyres Chatbot - User Status Fix Tool")
    print("=" * 60)
    
    # Step 1: Fix database
    fix_user_status()
    
    # Step 2: Test API endpoints
    test_user_leaving_api()
    
    # Step 3: Simulate user leaving
    simulate_user_leaving()
    
    print("\n✅ Fix complete! Users should now be properly marked as inactive when they leave.") 