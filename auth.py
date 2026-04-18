# ==========================================================
# AUTH MODULE
# PASSWORD HASHING + JWT AUTHENTICATION
# ==========================================================

import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Request

# ==========================================================
# CONFIGURATION
# ==========================================================

SECRET_KEY = "ultra_secure_secret_key_change_this"
ALGORITHM = "HS256"

TOKEN_EXPIRE_HOURS = 12


# ==========================================================
# PASSWORD HASHING
# ==========================================================

def hash_password(password: str) -> str:

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    return hashed.decode()


def verify_password(password: str, hashed_password: str) -> bool:

    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )


# ==========================================================
# JWT TOKEN CREATION
# ==========================================================

def create_token(username: str, role: str):

    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)

    payload = {
        "username": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


# ==========================================================
# JWT TOKEN VALIDATION
# ==========================================================

def verify_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except:
        return None


# ==========================================================
# GET CURRENT USER
# ==========================================================

def get_current_user(request: Request):

    token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload


# ==========================================================
# REQUIRE ADMIN ROLE
# ==========================================================

def require_admin(request: Request):

    user = get_current_user(request)

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user