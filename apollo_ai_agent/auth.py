import os
import asyncio
import requests
from httpx_oauth.clients.google import GoogleOAuth2
from db_functions import store_user_in_db
from dotenv import load_dotenv
from auth_utils import generate_referral_code
from db_functions import store_user_in_db, verify_user_credentials_google  # make sure this function exists

# Load environment variables
load_dotenv(".env")

# Google OAuth Credentials
CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REDIRECT_URI = "https://chat.realtyseek.ai/google-callback"

print(f"Google Client ID: {CLIENT_ID} and Google Client Secret {CLIENT_SECRET} and Redirect URI {REDIRECT_URI}")

# Initialize Google OAuth Client
client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)

# Function to get Google OAuth Authorization URL
async def get_google_auth_url():
    return await client.get_authorization_url(REDIRECT_URI, scope=["profile", "email"])

# Function to handle Google Signup/Login
async def handle_google_signup(code):
    """Handles Google OAuth callback, fetches user info & stores user if new."""
    return await process_google_login(code, login_type="Google")

async def handle_google_login(code):
    """Handles Google OAuth callback for login."""
    return await process_google_login(code, login_type="Google")

# Main logic for processing Google OAuth response
async def process_google_login(code, login_type):
    """Unified Google Login & Signup – handles both cases gracefully."""
    try:
        token = await client.get_access_token(code, REDIRECT_URI)
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        response = requests.get(user_info_url, headers=headers)

        if response.status_code != 200:
            print(f"⚠️ Google response error: {response.text}")
            return False, None

        user_data = response.json()
        user_id = user_data.get("id")
        user_email = user_data.get("email")
        user_name = user_data.get("name", "N/A")

        # Attempt to store user – if exists, silently continue
        my_code = generate_referral_code(user_name)
        _ = store_user_in_db(
            user_id=user_id,
            name=user_name,
            email=user_email,
            mobile=None,
            city=None,
            interests=None,
            password=None,
            login_type=login_type,
            my_code=my_code,
            referral_code=None
        )

        # Always fetch user and return full profile with token
        user = verify_user_credentials_google(user_email)
        return True, user

    except Exception as e:
        print(f"⚠️ Google Login/Signup Failed: {e}")
        return False, None


