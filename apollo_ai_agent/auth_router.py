import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Body, Depends
import mysql
from pydantic import BaseModel, constr
from mysql.connector import Error as MySQLError
import httpx 
import os
from dotenv import load_dotenv

load_dotenv('./../.env', override=True)
#RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")  # Securely load from .env
RECAPTCHA_SECRET_KEY='6LceOhgrAAAAADtQIfP9wYpFuH4gjBObrboExIz1'

from db_functions import (
    insert_referred_lead,
    is_mobile_already_referred,
    is_mobile_registered,
    store_user_in_db,
    verify_user_credentials,
    get_db_connection,
    insert_referral_lead_after_signup
)
from auth import get_google_auth_url, process_google_login
from auth_utils import (
    generate_referral_code, 
    generate_jwt_token, 
    generate_refresh_token, 
    JWT_SECRET,
    verify_jwt_token
)
import jwt

# -------------------------------
# Router & Logging Setup
# -------------------------------
router = APIRouter(prefix="/api", tags=["Authentication"])

logging.basicConfig(
    filename="auth_failures.log",
    level=logging.WARNING,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------------------------------
# Request Models
# -------------------------------
class SignupRequest(BaseModel):
    name: str
    email: str
    mobile: str
    city: Optional[str] = None
    interests: Optional[str] = None
    password: str
    referralCode: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class CompleteProfileRequest(BaseModel):
    user_id: str
    mobile_number: constr(min_length=10, max_length=15)
    referral_code: Optional[constr(min_length=8, max_length=8)] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# -------------------------------
# Signup Endpoint
# -------------------------------
@router.post("/signup")
async def signup(request: SignupRequest):
    my_code = generate_referral_code(request.name)
    incoming_referral_code = request.referralCode

    response = store_user_in_db(
        user_id=request.email,
        name=request.name,
        email=request.email,
        mobile=request.mobile,
        city=request.city,
        interests=request.interests,
        password=request.password,
        login_type="Email",
        my_code=my_code,
        referral_code=incoming_referral_code
    )

    if not response.get("success"):
        raise HTTPException(status_code=400, detail=response.get("message", "User signup failed."))

    if incoming_referral_code:
        insert_referral_lead_after_signup(
            user_id=request.email,
            referral_code=incoming_referral_code,
            profile_completed=True
        )

    print(f"✅ User signed up successfully: {request.email}")
    return {
        "success": True,
        "user": {
            "name": request.name,
            "email": request.email,
            "my_referral_code": my_code
        }
    }

# -------------------------------
# Login Endpoint
# -------------------------------
@router.post("/login")
async def login(request: LoginRequest, req: Request):
    user = verify_user_credentials(request.email, request.password)

    if user:
        user["email"] = user.get("email", request.email)
        access_token = generate_jwt_token(user)
        refresh_token = generate_refresh_token(user)
        user["token"] = access_token
        user["refresh_token"] = refresh_token
        print(f"User logged in successfully {request.email}")
        return {"success": True, "user": user}

    client_ip = req.client.host
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"FAILED LOGIN - Email: {request.email} | IP: {client_ip} | Time: {timestamp}"
    logging.warning(log_message)
    print(log_message)
    raise HTTPException(status_code=401, detail="Invalid credentials.")

# -------------------------------
# Google OAuth Endpoints
# -------------------------------
@router.get("/google-auth")
async def google_auth():
    auth_url = await get_google_auth_url()
    return {"url": auth_url}

@router.get("/google-callback")
async def google_callback(code: str):
    success, user_info = await process_google_login(code, login_type="Google")
    if success and user_info:
        access_token = generate_jwt_token(user_info)
        refresh_token = generate_refresh_token(user_info)
        user_info["token"] = access_token
        user_info["refresh_token"] = refresh_token
        return {"success": True, "user": user_info}
    else:
        raise HTTPException(status_code=400, detail="Google login failed")

# -------------------------------
# Refresh Token Endpoint
# -------------------------------
@router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, JWT_SECRET, algorithms=["HS256"])
        # Optionally, fetch and validate the user from the DB using payload["user_id"].
        user = {
            "user_id": payload["user_id"],
            "name": payload["name"],
            "email_id": payload["email"]
        }
        new_access_token = generate_jwt_token(user)
        new_refresh_token = generate_refresh_token(user)
        return {"access_token": new_access_token, "refresh_token": new_refresh_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

# -------------------------------
# JWT Validation Dependency & Protected Endpoint
# -------------------------------
def jwt_required(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing or invalid"
        )
    token = auth_header.split(" ")[1]
    print("Extracted token:", token)  # Logging the token
    payload = verify_jwt_token(token)
    print("Decoded payload:", payload)  # Logging the decoded payload
    return payload

@router.get("/protected")
async def protected_route(current_user: dict = Depends(jwt_required)):
    return {"success": True, "message": "Access granted to protected route", "user": current_user}

@router.patch("/complete-profile")
async def complete_profile(request: CompleteProfileRequest, current_user: dict = Depends(jwt_required)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 🔍 Retrieve the existing mobile number and referral info
        cursor.execute("SELECT mobile_number, referer_code FROM genai.users WHERE user_id = %s;", (request.user_id,))
        existing_data = cursor.fetchone()

        if not existing_data:
            return {"success": False, "message": "User not found."}

        # ❌ If mobile number already exists, do not allow update.
        if existing_data.get("mobile_number"):
            return {"success": False, "message": "Mobile number already set. Cannot be updated."}

        # Determine which referral code to use:
        # If the user already has a referer_code, ignore the request's referral_code.
        # Otherwise, if a referral code is provided in the request, validate it.
        referral_to_use = None
        if existing_data.get("referer_code"):
            referral_to_use = existing_data.get("referer_code")
        else:
            if request.referral_code:
                # Validate the provided referral code.
                cursor.execute("SELECT user_id FROM genai.users WHERE my_referral_code = %s;", (request.referral_code,))
                valid_referrer = cursor.fetchone()
                if not valid_referrer:
                    return {"success": False, "message": "Invalid referral code."}
                referral_to_use = request.referral_code
            else:
                referral_to_use = None

        # ✅ Check if mobile number is already used by another user
        cursor.execute("SELECT user_id FROM genai.users WHERE mobile_number = %s;", (request.mobile_number,))
        mobile_in_use = cursor.fetchone()
        if mobile_in_use and mobile_in_use["user_id"] != request.user_id:
            return {"success": False, "message": "Mobile number is already linked to another account."}

        # ✅ Perform the update: update mobile number and set referer_code (if not already set)
        cursor.execute("""
            UPDATE genai.users
            SET mobile_number = %s, referer_code = %s
            WHERE user_id = %s;
        """, (request.mobile_number, referral_to_use, request.user_id))
        conn.commit()

        print(f"✅ Completed profile for {request.user_id} - Mobile: {request.mobile_number}, Referral: {referral_to_use}")

        # ✅ Track referral lead only if a new referral code was provided (when previously not set)
        if referral_to_use and not existing_data.get("referer_code"):
            insert_referral_lead_after_signup(
                user_id=request.user_id,
                referral_code=referral_to_use,
                profile_completed=True
            )

        return {
            "success": True,
            "message": "Profile completed successfully.",
            "user": {
                "user_id": request.user_id,
                "mobile_number": request.mobile_number,
                "referral_code": referral_to_use
            }
        }

    except MySQLError as e:
        print(f"⚠️ DB Error during profile update: {e}")
        return {"success": False, "message": "Database error occurred."}

    finally:
        cursor.close()
        conn.close()

# -------------------------------
# Get My Referrals
# -------------------------------
@router.get("/my-referrals")
async def get_my_referrals(
    current_user: Dict[str, Any] = Depends(jwt_required)
):
    """
    Returns:
      - code_referrals: users who joined via your referral code
      - lead_referrals: property leads you have submitted
    """
    user_id = current_user["user_id"]

    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # 1) fetch your own referral code
                cursor.execute(
                    "SELECT my_referral_code FROM genai.users WHERE user_id = %s",
                    (user_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "message": "User not found."}
                my_code = row["my_referral_code"]

                # 2) fetch code-based referrals
                cursor.execute("""
                    SELECT
                      rl.referred_user_id,
                      u.name,
                      rl.joined_on,
                      rl.updated_at,
                      rl.transaction_status,
                      rl.partner_updates,
                      rl.notes
                    FROM genai.referral_leads rl
                    LEFT JOIN genai.users u
                      ON rl.referred_user_id = u.user_id
                    WHERE rl.referrer_user_id = %s
                    ORDER BY rl.joined_on DESC
                """, (user_id,))
                code_referrals = cursor.fetchall()

                # 3) fetch property leads YOU submitted
                cursor.execute("""
                    SELECT
                      id,
                      name,
                      mobile,
                      intent,
                      property_description,
                      note,
                      created_at,
                      updated_at,
                      referral_status,
                      reward_site_visit,
                      reward_deal_closure
                    FROM genai.referred_leads
                    WHERE referrer_user_id = %s
                    ORDER BY created_at DESC
                """, (user_id,))
                lead_referrals = cursor.fetchall()

        return {
            "success": True,
            "my_referral_code": my_code,
            "total_code_referrals": len(code_referrals),
            "code_referrals": code_referrals,
            "total_lead_referrals": len(lead_referrals),
            "lead_referrals": lead_referrals
        }

    except Exception as e:
        print(f"⚠️ Error in /my-referrals: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch referral data")
            

class UpdateReferralRequest(BaseModel):
    user_id: str
    referral_code: constr(min_length=8, max_length=8)

@router.patch("/update-referral")
async def update_referral(request: UpdateReferralRequest, current_user: dict = Depends(jwt_required)):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Check if user exists and referral is already set
        cursor.execute("SELECT referer_code FROM genai.users WHERE user_id = %s;", (request.user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found.")
        if user_data.get("referer_code"):
            raise HTTPException(status_code=400, detail="Referral code already set.")

        # Step 2: Validate referral code exists in users table
        cursor.execute("SELECT user_id FROM genai.users WHERE my_referral_code = %s;", (request.referral_code,))
        valid_referrer = cursor.fetchone()
        if not valid_referrer:
            raise HTTPException(status_code=400, detail="Invalid referral code.")

        # Step 3: Update the user's referer_code
        cursor.execute(
            "UPDATE genai.users SET referer_code = %s WHERE user_id = %s;",
            (request.referral_code, request.user_id)
        )
        conn.commit()

        print(f"✅ Referral code {request.referral_code} set for user {request.user_id}")

        # Step 4: Insert referral lead if not already present
        insert_referral_lead_after_signup(
            user_id=request.user_id,
            referral_code=request.referral_code,
            profile_completed=False  # Mark as incomplete; will be completed on mobile update
        )

        return {"success": True, "message": "Referral code updated and lead recorded."}

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    finally:
        cursor.close()
        conn.close()

# Request Model for Referral Lead (updated field names)
class ReferLeadRequest(BaseModel):
    name: str
    mobile: str
    city: str  # ✅ New Field
    intent: str
    property_description: Optional[str] = None
    note: Optional[str] = None
    recaptcha_token: Optional[str] = None

# New API Endpoint: /api/refer-lead
@router.post("/refer-lead")
async def refer_lead(
    request_data: ReferLeadRequest,
    current_user: dict = Depends(jwt_required)
):
    try:
        # ✅ Step 1: Validate reCAPTCHA token
        if not request_data.recaptcha_token:
            raise HTTPException(status_code=400, detail="reCAPTCHA token missing.")

        async with httpx.AsyncClient() as client:
            google_response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": RECAPTCHA_SECRET_KEY,
                    "response": request_data.recaptcha_token
                }
            )

        verification_result = google_response.json()
        if not verification_result.get("success") or verification_result.get("score", 0) < 0.5:
            logging.warning(f"🔒 reCAPTCHA verification failed: {verification_result}")
            raise HTTPException(status_code=400, detail="Human user verification failed. Please try again.")

        # ✅ Step 2: Check duplicate mobile number
        if is_mobile_registered(request_data.mobile):
            return {
                "success": False,
                "message": f"The mobile number {request_data.mobile} already exists as a registered user. Please refer others."
            }

        if is_mobile_already_referred(request_data.mobile):
            return {
                "success": False,
                "message": f"The mobile number {request_data.mobile} has already been submitted as a referral. Please refer others."
            }

        # ✅ Step 3: Insert referral lead
        success = insert_referred_lead(
            referrer_user_id=current_user.get("user_id"),
            name=request_data.name,
            mobile=request_data.mobile,
            city=request_data.city,  # ✅ NEW FIELD
            intent=request_data.intent,
            property_description=request_data.property_description,
            note=request_data.note
        )

        if not success:
            return {
                "success": False,
                "message": "An error occurred while saving your referral lead. Please try again later."
            }

        logging.info(f"✅ Referral lead submitted for mobile {request_data.mobile}")
        return {"success": True, "message": "Referral lead submitted successfully."}

    except Exception as e:
        logging.error(f"❌ Error inserting referral lead: {e}")
        return {"success": False, "message": f"Error inserting referral lead: {str(e)}"}

