from datetime import datetime, timedelta, timezone
from typing import Optional
from backend.app.core.security import create_access_token, decode_access_token
from backend.app.schemas.auth import TokenData

def generate_token_for_user(user_id: str, username: str, role: str, company_id: Optional[str] = None) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "company_id": company_id
    }
    return create_access_token(payload)

def parse_token(token: str) -> Optional[TokenData]:
    payload = decode_access_token(token)
    if not payload:
        return None
    return TokenData(
        user_id=payload.get("sub"),
        username=payload.get("username"),
        role=payload.get("role"),
        company_id=payload.get("company_id")
    )
