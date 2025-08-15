import os
import jwt
import datetime
import string
import random
from fastapi import HTTPException, status

JWT_SECRET = os.environ.get("JWT_SECRET", "supersecret")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # 1 hour expiration for access token
JWT_REFRESH_EXP_DELTA_SECONDS = 604800  # 7 days expiration for refresh token

def generate_jwt_token(user: dict) -> str:
    """
    Generates an access JWT token for a logged-in user.
    Expects the user dict to contain 'user_id', 'name', and 'email_id'.
    """
    payload = {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email_id"],
        "exp": datetime.datetime.now() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def generate_refresh_token(user: dict) -> str:
    """
    Generates a refresh token for a logged-in user.
    This token lasts longer than the access token.
    """
    payload = {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email_id"],
        "exp": datetime.datetime.now() + datetime.timedelta(seconds=JWT_REFRESH_EXP_DELTA_SECONDS)
    }
    refresh_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return refresh_token

def verify_jwt_token(token: str):
    """
    Verifies the provided JWT access token. If invalid or expired, raises an HTTPException.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

def generate_referral_code(name: str) -> str:
    prefix = name[:2].upper() if name and len(name) >= 2 else 'XX'
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return prefix + suffix
