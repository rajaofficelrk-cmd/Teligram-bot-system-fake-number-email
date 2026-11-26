# RK RAJA ULTIMATE XWD

A GitHub-ready Telegram group and utility bot built with Python + aiogram 3.

## Features included
- Start/help/menu, user ID, profile and bot statistics
- SQLite user/group settings, warnings and notes
- Group title lock/unlock/status (requires bot admin permission to change group info)
- Anti-link, anti-flood, welcome/goodbye, rules, notes and moderation commands
- Owner-only broadcast and bot status controls
- Text utilities, password generator, dice/coin/number games
- Optional AI chat through an OpenAI-compatible API

## Not included as fake features
Virtual phone numbers, SMS inboxes, disposable email inboxes, image generation and downloaders need a real provider/API and their terms must be followed. This repository does not claim those integrations work without provider credentials. It does not collect or forward private login/verification codes.

## Deploy
1. Create a Telegram bot with BotFather and copy its token.
2. Copy `.env.example` to `.env` and set `BOT_TOKEN` and numeric `OWNER_ID`. Do not upload `.env` to GitHub.
3. On a Linux hosting service use Python 3.11+.
4. Install: `pip install -r requirements.txt`
5. Run: `python -m bot.main`

Set the bot as group administrator with permission to manage group info, delete messages, restrict members, and invite users only if you want those features. Telegram group owners and other admins may still have higher permissions than the bot.

## Commands
- `/start`, `/help`, `/menu`, `/id`, `/profile`, `/stats`, `/about`
- `/gclock`, `/gcunlock`, `/setgclock <title>`, `/lockstatus`
- `/antilink on|off`, `/antiflood on|off`, `/welcome on|off`, `/setwelcome <text>`
- `/rules`, `/setrules <text>`, `/note <name> <text>`, `/get <name>`, `/notes`
- `/warn` (reply), `/warnings` (reply), `/clearwarns` (reply), `/kick` (reply), `/ban` (reply), `/unban <user_id>`, `/mute <minutes>` (reply), `/unmute` (reply)
- `/pin` (reply), `/unpin`, `/del` (reply)
- `/broadcast <message>` (owner only), `/ai <message>` (if AI configured)
- `/coin`, `/dice`, `/roll <max>`, `/password`, `/upper`, `/lower`, `/reverse`, `/count`

Some commands require admin rights and only work in groups/supergroups.
