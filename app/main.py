import asyncio
import uuid
from urllib.parse import urlencode
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message, Update
from .config import settings
from .db import db
from .security import issue_session, verify_session
from . import keyboards as kb, messages as msg

app = FastAPI(title="Telegram Game Hub")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.allowed_origins), allow_methods=["GET","POST"], allow_headers=["*"])
bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)) if settings.bot_token else None
dp = Dispatcher()

async def edit(query: CallbackQuery, text: str, markup):
    await query.message.edit_text(text, reply_markup=markup)
    await query.answer()

@dp.message(Command("start", "menu"))
async def start(message: Message): await message.answer(msg.WELCOME, reply_markup=kb.main_menu())

@dp.callback_query(F.data == "menu:home")
async def home(q: CallbackQuery): await edit(q, msg.WELCOME, kb.main_menu())
@dp.callback_query(F.data == "menu:games")
async def games(q: CallbackQuery): await edit(q, msg.GAMES, kb.games_menu())
@dp.callback_query(F.data == "game:doodle_covert")
async def game_info(q: CallbackQuery): await edit(q, msg.DOODLE, kb.game_details())
@dp.callback_query(F.data == "game:send:doodle_covert")
async def send_game(q: CallbackQuery):
    await q.answer()
    await bot.send_game(q.from_user.id, settings.game_short_name, reply_markup=kb.native_game())
@dp.callback_query(F.data == "menu:settings")
async def settings_page(q: CallbackQuery): await edit(q, msg.SETTINGS, kb.back_home())
@dp.callback_query(F.data.in_({"menu:rankings","rank:doodle_covert"}))
async def rankings(q: CallbackQuery):
    rows = await db.leaderboard("doodle_covert", 5) if db.ready else []
    lines = [f"{i}. {r['display_name']} — {r['best_score']}" for i,r in enumerate(rows,1)] or ["No scores yet."]
    await edit(q, msg.quote("Doodle Covert — Top 5\n\n" + "\n".join(lines)), kb.back_home())
@dp.callback_query(F.data == "menu:profile")
async def profile(q: CallbackQuery): await edit(q, msg.quote(f"Agent Profile\n\n{q.from_user.full_name}\nTelegram ID: {q.from_user.id}"), kb.back_home())
@dp.callback_query(F.data == "menu:feedback")
async def feedback_help(q: CallbackQuery): await edit(q, msg.quote("Feedback\n\nSend /feedback followed by your message. Example:\n/feedback The guard turn feels too fast"), kb.back_home())
@dp.message(Command("feedback"))
async def feedback_command(message: Message):
    text = message.text.partition(" ")[2].strip()
    if not text: return await message.reply(msg.quote("Add your feedback after /feedback."))
    if db.ready: await db.request("POST", "feedback", json={"telegram_user_id":message.from_user.id,"game_key":"hub","message":text})
    await message.reply(msg.quote("Feedback saved. Thank you."))

@dp.callback_query(F.game_short_name)
async def launch_game(q: CallbackQuery):
    user = {"id":q.from_user.id,"username":q.from_user.username,"display_name":q.from_user.full_name}
    if db.ready: await db.upsert_player(user)
    jti = str(uuid.uuid4())
    claims = {"sub":str(q.from_user.id),"jti":jti,"game_key":"doodle_covert","chat_id":q.message.chat.id if q.message else None,"message_id":q.message.message_id if q.message else None,"inline_message_id":q.inline_message_id,"display_name":q.from_user.full_name}
    token = issue_session(**claims)
    if db.ready: await db.save_session({"jti":jti,"telegram_user_id":q.from_user.id,"game_key":"doodle_covert","chat_id":claims["chat_id"],"message_id":claims["message_id"],"inline_message_id":claims["inline_message_id"]})
    url = settings.game_url + "?" + urlencode({"session":token,"api":settings.public_url,"player_name":q.from_user.full_name})
    await q.answer(url=url)

class Score(BaseModel):
    game_key: str
    score: int = Field(ge=0)
    won: bool
    sector: int = Field(ge=1, le=999)
    intel: int = Field(ge=0, le=3)
    time_seconds: float = Field(ge=0, le=86400)
    detections: int = Field(ge=0, le=999)
class Feedback(BaseModel):
    game_key: str
    message: str = Field(min_length=1, max_length=2000)

def claims_from(auth: str | None):
    if not auth or not auth.startswith("Bearer "): raise HTTPException(401, "Missing game session")
    try: return verify_session(auth[7:])
    except Exception: raise HTTPException(401, "Invalid or expired game session")

@app.post("/api/v1/scores")
async def score(body: Score, authorization: str | None = Header(None)):
    claims = claims_from(authorization)
    if body.game_key != claims["game_key"] or body.score > body.sector * 1350: raise HTTPException(400, "Invalid score")
    best = await db.record_score(int(claims["sub"]), body.model_dump())
    args = {"user_id":int(claims["sub"]),"score":best,"force":False}
    if claims.get("inline_message_id"): args["inline_message_id"] = claims["inline_message_id"]
    else: args.update(chat_id=claims["chat_id"], message_id=claims["message_id"])
    await bot.set_game_score(**args)
    return {"ok":True,"best_score":best}

@app.get("/api/v1/leaderboard")
async def leaderboard(game: str="doodle_covert", limit: int=5): return {"entries":await db.leaderboard(game, min(max(limit,1),100))}
@app.post("/api/v1/feedback")
async def feedback(body: Feedback, authorization: str | None = Header(None)):
    claims = claims_from(authorization)
    await db.request("POST", "feedback", json={"telegram_user_id":int(claims["sub"]),**body.model_dump()})
    if settings.owner_id: await bot.send_message(settings.owner_id, msg.quote(f"Game feedback from {claims.get('display_name','Agent')}:\n\n{body.message}"))
    return {"ok":True}
@app.get("/health")
async def health(): return {"ok":True,"database":db.ready}
@app.post("/telegram/webhook")
async def webhook(request: Request, x_telegram_bot_api_secret_token: str | None=Header(None)):
    if x_telegram_bot_api_secret_token != settings.webhook_secret: raise HTTPException(403)
    await dp.feed_update(bot, Update.model_validate(await request.json(), context={"bot":bot}))
    return {"ok":True}
@app.on_event("startup")
async def startup():
    if bot: await bot.set_webhook(settings.public_url + "/telegram/webhook", secret_token=settings.webhook_secret)
@app.on_event("shutdown")
async def shutdown():
    if bot: await bot.session.close()
