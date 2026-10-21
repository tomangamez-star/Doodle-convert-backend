from datetime import datetime, timezone
from typing import Any
import httpx
from .config import settings

class Database:
    def __init__(self):
        self.base = f"{settings.supabase_url}/rest/v1"
        self.headers = {"apikey": settings.supabase_key, "Authorization": f"Bearer {settings.supabase_key}", "Content-Type": "application/json"}

    @property
    def ready(self): return bool(settings.supabase_url and settings.supabase_key)

    async def request(self, method: str, table: str, *, params=None, json=None, prefer="return=representation") -> Any:
        if not self.ready: raise RuntimeError("Supabase is not configured")
        headers = {**self.headers, "Prefer": prefer}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.request(method, f"{self.base}/{table}", params=params, json=json, headers=headers)
            response.raise_for_status()
            return response.json() if response.content else None

    async def upsert_player(self, user: dict):
        now = datetime.now(timezone.utc).isoformat()
        payload = {"telegram_user_id": user["id"], "username": user.get("username"), "display_name": user.get("display_name") or "Agent", "last_seen": now}
        return await self.request("POST", "players", params={"on_conflict":"telegram_user_id"}, json=payload, prefer="resolution=merge-duplicates,return=representation")

    async def save_session(self, payload): return await self.request("POST", "game_sessions", json=payload)

    async def record_score(self, user_id: int, body: dict):
        run = {"telegram_user_id":user_id, **{k:body[k] for k in ("game_key","score","won","sector","intel","time_seconds","detections")}}
        await self.request("POST", "game_scores", json=run)
        current = await self.request("GET", "player_bests", params={"telegram_user_id":f"eq.{user_id}","game_key":f"eq.{body['game_key']}","select":"*"})
        old = current[0] if current else {}
        best = max(int(old.get("best_score", 0)), int(body["score"]))
        payload = {"telegram_user_id":user_id,"game_key":body["game_key"],"best_score":best,"total_runs":int(old.get("total_runs",0))+1,"total_wins":int(old.get("total_wins",0))+int(bool(body["won"])),"updated_at":datetime.now(timezone.utc).isoformat()}
        await self.request("POST", "player_bests", params={"on_conflict":"telegram_user_id,game_key"}, json=payload, prefer="resolution=merge-duplicates,return=minimal")
        return best

    async def leaderboard(self, game: str, limit: int):
        return await self.request("GET", "leaderboard", params={"game_key":f"eq.{game}","select":"display_name,best_score","order":"best_score.desc","limit":str(limit)})

db = Database()
