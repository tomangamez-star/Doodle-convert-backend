import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "change-me")
    session_secret: str = os.getenv("SESSION_SECRET", "change-me-too")
    public_url: str = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000").rstrip("/")
    game_url: str = os.getenv("GAME_BASE_URL", "").rstrip("/")
    game_short_name: str = os.getenv("DOODLE_GAME_SHORT_NAME", "doodle_covert")
    supabase_url: str = os.getenv("SUPABASE_URL", "").rstrip("/")
    supabase_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    allowed_origins: tuple[str, ...] = tuple(x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip())
    owner_id: int = int(os.getenv("OWNER_ID", "0") or 0)

settings = Settings()
