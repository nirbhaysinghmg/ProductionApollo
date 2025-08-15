from typing import Optional
import mysql.connector
import json
import hashlib
from auth_utils import generate_jwt_token

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123$Ubuntu",
    "database": "gurgaon"
}

def get_db_connection():
    """Establish a database connection."""
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    """Ensure required tables exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    create_chat_table = """
    CREATE TABLE IF NOT EXISTS user_chat_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(100) NOT NULL,
        session_id VARCHAR(100) NOT NULL DEFAULT 'default_session',
        role ENUM('user', 'assistant') NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    create_queries_table = """
    CREATE TABLE IF NOT EXISTS user_queries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(100) NOT NULL,
        user_input TEXT NOT NULL,
        category ENUM('generic_query', 'city_level_query', 'micro_market_level_query', 'sector_level_query', 
                      'project_query', 'price_query', 'new_launch_query', 'investment_query', 'irrelevant_query') NOT NULL,
        normalized_input TEXT NOT NULL,
        sql_query TEXT,
        updated_context TEXT,
        context TEXT,
        full_response TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    create_tracking_table = """
    CREATE TABLE IF NOT EXISTS user_tracking (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id VARCHAR(100) NOT NULL,
        name VARCHAR(100),
        mobile VARCHAR(20),
        user_input TEXT NOT NULL,
        category VARCHAR(100) NOT NULL,
        normalized_input TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    cursor.execute(create_chat_table)
    cursor.execute(create_queries_table)
    cursor.execute(create_tracking_table)
    conn.commit()
    cursor.close()
    conn.close()

def load_chat_history_from_db(user_id):
    """Retrieve chat history from MySQL for a given user_id."""
    chat_history = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT role, message FROM user_chat_history
            WHERE user_id = %s ORDER BY timestamp ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        chat_history = [{"role": row["role"], "message": row["message"]} for row in rows]
        print(f"🔄 Loaded chat history for {user_id}: {chat_history}")  # Debug log
    except Exception as e:
        print(f"⚠️ Error loading chat history: {e}")
    return chat_history

def save_chat_history_to_db(user_id, role, message, session_id="default_session"):
    """Store chat history into MySQL for a given user_id."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_chat_history (user_id, session_id, role, message)
            VALUES (%s, %s, %s, %s)
        """, (user_id, session_id, role, message))
        conn.commit()
        conn.close()
        print(f"✅ Chat history saved for {user_id} -> {role}: {message[:100]} [Session: {session_id}]")
    except Exception as e:
        print(f"❌ Error saving chat history: {e}")

def save_user_query(user_id, user_input, category, normalized_input, sql_query, updated_context, context, full_response):
    """Save user interaction to the `user_queries` table, avoiding duplicates."""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM user_queries 
            WHERE user_id = %s AND user_input = %s AND category = %s AND sql_query = %s LIMIT 1
        """, (user_id, user_input, category, sql_query))
        existing = cursor.fetchone()

        if not existing:
            insert_query = """
            INSERT INTO user_queries 
            (user_id, user_input, category, normalized_input, sql_query, updated_context, context, full_response) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (user_id, user_input, category, normalized_input, sql_query, 
                                          json.dumps(updated_context), context, full_response))
            conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error saving user query: {e}")

def save_user_tracking(user_id, name, mobile, user_input, category, normalized_input):
    """Save user interaction to the `user_tracking` table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO user_tracking (user_id, name, mobile, user_input, category, normalized_input)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (user_id, name, mobile, user_input, category, normalized_input))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ User tracking saved for {user_id}")
    except Exception as e:
        print(f"❌ Error saving user tracking: {e}")
        
def store_user_in_db(user_id, name, email, mobile, city, interests, password=None, login_type="Email", my_code=None, referral_code=None):
    """
    Stores a new user in the database if they do not already exist.
    Validates that any provided referral code exists in the system.
    
    Returns a dictionary with keys 'success' (bool) and 'message' (str).
    """
    try:
        print(f"🔍 Checking if user {user_id} ({email}) exists in database...")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Validate referral code if provided
        if referral_code:
            cursor.execute("""
                SELECT user_id FROM genai.users 
                WHERE my_referral_code = %s LIMIT 1;
            """, (referral_code,))
            referrer = cursor.fetchone()
            if not referrer:
                print(f"⚠️ Invalid referral code: {referral_code}")
                return {
                    "success": False,
                    "message": "Invalid referral code. Please enter a valid one or sign up without it."
                }

        # ✅ Hash password for Email login
        if password and login_type == "Email":
            import hashlib
            password = hashlib.sha256(password.encode()).hexdigest()

        mobile = mobile if mobile else None

        # ✅ Insert new user
        insert_query = """
            INSERT INTO genai.users 
            (user_id, name, email_id, mobile_number, city, interests, password, login_type, my_referral_code, referer_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            insert_query,
            (user_id, name, email, mobile, city, interests, password, login_type, my_code, referral_code)
        )
        conn.commit()

        print(f"✅ User inserted: {email}")
        return {"success": True, "message": "User stored successfully."}

    except mysql.connector.IntegrityError as e:
        msg = str(e)
        if "mobile_number" in msg:
            return {"success": False, "message": "Mobile number already linked to another account."}
        elif "user_id" in msg or "PRIMARY" in msg:
            return {"success": False, "message": "An account already exists with this email. Please login instead."}
        return {"success": False, "message": "Signup failed due to duplicate data."}

    except mysql.connector.Error as err:
        print(f"⚠️ Database error: {err}")
        return {"success": False, "message": f"Database error: {err}"}

    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return {"success": False, "message": "Unexpected error during signup."}

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


        
# Ensure tables exist on import
create_tables()

### JWT and React additions
import os
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(".env")

def verify_user_credentials(email, password):
    """
    Verifies user credentials and returns user object with JWT token if valid.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, name, mobile_number, email_id, city, area, ui_mode, my_referral_code, password
            FROM genai.users 
            WHERE email_id = %s LIMIT 1;
        """, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return None

        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        if user.get("password") != hashed_input_password:
            return None

        token = generate_jwt_token(user)
        user["token"] = token
        del user["password"]
        return user
    except Exception as e:
        print(f"Error verifying user credentials: {e}")
        return None


def clear_chat_history_from_db(user_id, session_id="default_session"):
    """Clear chat history for a given user and session."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM user_chat_history
            WHERE user_id = %s AND session_id = %s
        """, (user_id, session_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Chat history cleared for {user_id} [Session: {session_id}]")
        return True
    except Exception as e:
        print(f"❌ Error clearing chat history for {user_id}: {e}")
        return False

def save_user_feedback(user_id, name, mobile, feedback_type, rating, user_input, response, comment):
    """Save user feedback into the user_feedback table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO user_feedback (user_id, name, mobile, feedback_type, rating, user_input, response, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (user_id, name, mobile, feedback_type, rating, user_input, response, comment))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error saving feedback: {e}")
        return False

def verify_user_credentials_google(email):
    """Fetch user by email (Google Login doesn't need password)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, name, mobile_number, email_id, city, area, ui_mode, my_referral_code
            FROM genai.users WHERE email_id = %s LIMIT 1;
        """, (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return None

        token = generate_jwt_token(user)
        user["token"] = token
        return user
    except Exception as e:
        print(f"Error verifying Google login: {e}")
        return None

def insert_referral_lead_after_signup(user_id: str, referral_code: str, profile_completed: bool = False):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get referrer user_id using referral code
        cursor.execute("SELECT user_id FROM genai.users WHERE my_referral_code = %s;", (referral_code,))
        referrer = cursor.fetchone()
        if not referrer:
            print(f"⚠️ Invalid referral code: {referral_code}")
            return

        referrer_id = referrer[0]

        # Avoid duplicates
        cursor.execute("SELECT id FROM genai.referral_leads WHERE referred_user_id = %s;", (user_id,))
        if cursor.fetchone():
            print(f"ℹ️ Referral lead already exists for {user_id}")
            return

        cursor.execute("""
            INSERT INTO genai.referral_leads (
                referred_user_id,
                referrer_user_id,
                referral_code_used,
                profile_completed
            ) VALUES (%s, %s, %s, %s);
        """, (user_id, referrer_id, referral_code, profile_completed))

        conn.commit()
        print(f"✅ Referral lead inserted for {user_id} (referrer: {referrer_id})")

    except Exception as e:
        print(f"❌ Error inserting referral lead: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def is_mobile_registered(mobile: str) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM genai.users WHERE mobile_number = %s;", (mobile,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error in is_mobile_registered: {e}")
        return False


def is_mobile_already_referred(mobile: str) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM genai.referred_leads WHERE mobile = %s;", (mobile,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Exception as e:
        print(f"Error in is_mobile_already_referred: {e}")
        return False

def insert_referred_lead(
    referrer_user_id: str,
    name: str,
    mobile: str,
    city: str,  # ✅ NEW FIELD
    intent: str,
    property_description: Optional[str],
    note: Optional[str]
) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO genai.referred_leads
            (referrer_user_id, name, mobile, city, intent, property_description, note,
             referral_status, reward_site_visit, reward_deal_closure, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'submitted', 'pending', 'pending', NOW(), NOW());
        """
        cursor.execute(sql, (
            referrer_user_id,
            name,
            mobile,
            city,
            intent,
            property_description,
            note
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting referred lead: {e}")
        return False

def insert_ai_agent_user(guest_id: str, mobile: str, agent_name: str, name: str = None):
    """Insert user details captured during AI agent conversation into ai_agent_users."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO ai_agent_users (guest_id, mobile, agent_name, name)
            VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (guest_id, mobile, agent_name, name))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ AI Agent user inserted: Guest ID = {guest_id}, Mobile = {mobile}, Name = {name}")
    except Exception as e:
        print(f"❌ Error inserting AI Agent user: {e}")

