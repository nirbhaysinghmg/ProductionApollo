import os
import jwt
import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
import mysql.connector
from db_functions import get_db_connection  # if used in register_guest

router = APIRouter(prefix="/api/guest", tags=["Guest Users"])

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600          # 1 hour for guest access token
JWT_REFRESH_EXP_DELTA_SECONDS = 604800  # 7 days for guest refresh token

def generate_guest_jwt_token(guest_id: str) -> str:
    payload = {
        "guest_id": guest_id,
        "user_type": "guest",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def generate_guest_refresh_token(guest_id: str) -> str:
    payload = {
        "guest_id": guest_id,
        "user_type": "guest",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_REFRESH_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

class GuestInfo(BaseModel):
    guest_id: str = Field(..., description="Unique guest ID from localStorage")
    name: str = Field(None, description="Guest name (optional at this stage)")
    mobile: str = Field(None, description="Guest mobile number (optional at this stage)")

@router.post("/register")
async def register_guest(info: GuestInfo):
    """
    Registers or updates a guest user in the database.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO guest_users (guest_id, name, mobile)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), mobile = VALUES(mobile)
        """
        cursor.execute(insert_query, (info.guest_id, info.name, info.mobile))
        conn.commit()
        cursor.close()
        conn.close()
        return {
            "success": True,
            "guest_id": info.guest_id,
            "message": "Guest registered/updated successfully"
        }
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

class GuestTokenRequest(BaseModel):
    guest_id: str = Field(..., description="Unique guest ID from localStorage")

@router.post("/token")
async def get_guest_token(request: GuestTokenRequest):
    """
    Generates an access token and refresh token for a guest user.
    """
    try:
        access_token = generate_guest_jwt_token(request.guest_id)
        refresh_token = generate_guest_refresh_token(request.guest_id)
        return {
            "success": True,
            "guest_id": request.guest_id,
            "token": access_token,
            "refresh_token": refresh_token
        }
    except Exception as err:
        print(f"Error generating token: {err}")
        raise HTTPException(status_code=500, detail=f"Error generating token: {err}")

class GuestRefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Guest refresh token")

@router.post("/refresh")
async def refresh_guest_token(request: GuestRefreshTokenRequest):
    """
    Accepts a guest refresh token and, if valid, returns new access and refresh tokens.
    """
    try:
        payload = jwt.decode(request.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        guest_id = payload.get("guest_id")
        if not guest_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        new_access_token = generate_guest_jwt_token(guest_id)
        new_refresh_token = generate_guest_refresh_token(guest_id)
        return {
            "success": True,
            "guest_id": guest_id,
            "token": new_access_token,
            "refresh_token": new_refresh_token
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired. Please request a new token.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

# -------------------------------
# Guest JWT Validation Dependency & Protected Endpoint
# -------------------------------
def guest_jwt_required(request: Request):
    """
    Dependency function to validate a guest JWT token.
    Checks for a valid Bearer token and ensures the token payload includes 'user_type' as 'guest'.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    token = auth_header.split(" ")[1]
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    if payload.get("user_type") != "guest":
        raise HTTPException(status_code=401, detail="Invalid guest token")
    return payload

@router.get("/protected")
async def guest_protected_route(current_guest: dict = Depends(guest_jwt_required)):
    """
    Protected endpoint for guest users.
    Accessible only with a valid guest JWT token.
    """
    return {
        "success": True,
        "message": "Access granted to guest protected route",
        "guest": current_guest
    }
