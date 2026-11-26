
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="help_menu")

HELP_TEXT = """
👑 **RK RAJA ULTIMATE XWD**

━━━━━━━━━━━━━━━━━━
🤖 **AI COMMANDS**
━━━━━━━━━━━━━━━━━━
/ai — AI se chat
/clearhistory — AI chat history clear
/profile — User profile
/setbio — Bio update
/setname — Display name update
/mystats — Activity stats
/topusers — Active users

━━━━━━━━━━━━━━━━━━
🛡️ **GROUP MANAGEMENT**
━━━━━━━━━━━━━━━━━━
/rules — Group rules
/setrules — Rules set
/antilink on/off — Link protection
/antiflood on/off — Flood protection
/welcome on/off — Welcome messages
/warn — Warn member
/resetwarn — Reset warning
/mute — Mute member
/unmute — Unmute member
/kick — Remove member
/ban — Ban member
/unban — Unban by user ID
/gclock — Lock group title
/gcunlock — Unlock group title

━━━━━━━━━━━━━━━━━━
📌 **NOTES**
━━━━━━━━━━━━━━━━━━
/save — Save note
/get — Get note
/notes — List notes
/clear — Delete note

━━━━━━━━━━━━━━━━━━
🎮 **GAMES**
━━━━━━━━━━━━━━━━━━
/rps — Rock paper scissors
/guess — Guess number
/answer — Submit guess
/quiz — Start quiz
/quizanswer — Quiz answer
/truth — Truth question
/dare — Safe dare
/joke — Random joke
/8ball — Ask 8ball

━━━━━━━━━━━━━━━━━━
🎉 **FUN**
━━━━━━━━━━━━━━━━━━
/coin — Flip coin
/dice — Roll dice
/random — Random number
/flip — Flip message
/choose — Choose option
/time — Server time
/love — Fun random score
/compliment — Compliment

━━━━━━━━━━━━━━━━━━
✍️ **TEXT TOOLS**
━━━━━━━━━━━━━━━━━━
/reverse — Reverse text
/uppercase — Uppercase
/lowercase — Lowercase
/titlecase — Title case
/count — Count text
/sha256 — Text hash
/password — Generate password
/username — Username idea
/clean — Clean spaces
/bold — Bold text
/italic — Italic text
/code — Code formatting

━━━━━━━━━━━━━━━━━━
✨ **GENERATORS**
━━━━━━━━━━━━━━━━━━
/nickname — Nickname idea
/teamname — Team name
/bio — Bio idea
/quote — Quote
/emoji — Emoji collection
/number — Random ID idea
/stylish — Stylish text
/fakechat — Fictional chat template

━━━━━━━━━━━━━━━━━━
📋 **TASKS & REMINDERS**
━━━━━━━━━━━━━━━━━━
/addtask — Add task
/mytasks — Show tasks
/done — Complete task
/deltask — Delete task
/remind — Set reminder

━━━━━━━━━━━━━━━━━━
⚙️ **GENERAL**
━━━━━━━━━━━━━━━━━━
/start — Start bot
/id — Telegram ID
/help — Show this menu

━━━━━━━━━━━━━━━━━━
👑 **RK RAJA ULTIMATE XWD**
"""

@router.message(Command("help", "commands", "menu"))
async def help_command(message: Message):
    await message.answer(HELP_TEXT)


@router.message(Command("about"))
async def about_command(message: Message):
    await message.answer(
        "👑 **RK RAJA ULTIMATE XWD**\n\n"
        "A modular Telegram assistant built with Python and aiogram.\n\n"
        "Features include AI chat, group management, notes, "
        "games, text tools, generators, tasks and reminders.\n\n"
        "Use /help to see the command directory."
    )
