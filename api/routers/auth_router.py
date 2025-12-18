from fastapi import APIRouter, HTTPException
from services.auth_service import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(username: str, password: str):
    # TEMP: replace with DB lookup + password hashing later
    if username != "admin" or password != "admin":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        user_id="user-123",
        role="admin",
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
