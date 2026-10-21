import time
import jwt
from .config import settings

def issue_session(**claims) -> str:
    now = int(time.time())
    return jwt.encode({**claims, "iat": now, "exp": now + 3600}, settings.session_secret, algorithm="HS256")

def verify_session(token: str) -> dict:
    return jwt.decode(token, settings.session_secret, algorithms=["HS256"])
