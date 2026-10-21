# Telegram Game Hub Bot

A Render-ready Telegram multi-game hub. It uses inline message buttons, native Telegram game cards, signed play sessions, Telegram game scores, a persistent Supabase leaderboard, profiles, and feedback.

The repository pins Render to Python 3.12.7 through `.python-version`. Keep this file in the repository root; Render's Python 3.14 default can otherwise force `pydantic-core` into an unsupported source build.

## One-time setup

1. In Supabase SQL Editor, run `supabase/schema.sql`.
2. In BotFather, use `/newgame`, select this bot, upload the game card artwork, and set the short name to the exact `DOODLE_GAME_SHORT_NAME` value (`doodle_covert` by default). The URL BotFather requests can be the GitHub Pages URL; launches are replaced with signed URLs by the bot.
3. Push this folder to its own repository and create a Render Blueprint using `render.yaml`.
4. Fill every secret/environment value shown in `.env.example`. Never place the Supabase service-role key in the game or GitHub Pages repository.
5. Set `GAME_BASE_URL` to the deployed game URL, including its trailing path. Set `ALLOWED_ORIGINS` to the GitHub Pages origin.
6. Open the bot and send `/start`.

The webhook is registered automatically at startup. `/health` reports whether the backend is running and Supabase is configured.

## Adding another game

Register it with BotFather, add its metadata/button and callback handler beside Doodle Covert, and store its own `game_key` and short name. The database schema already separates scores by game.

## Message behavior

Navigation uses inline buttons attached to bot messages, not the phone keyboard. Text is rendered as Telegram block quotes. The Play action sends a native Telegram game card. Telegram displays its own score strip after `setGameScore`; the bot's Rankings button reads the persistent global Top 5 from Supabase.
