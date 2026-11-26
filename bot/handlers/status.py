
import time
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import BOT_NAME, AI_API_KEY, OWNER_ID

router = Router(name="status")
START_TIME = time.monotonic()


@router.message(Command("ping"))
async def ping(message: Message):
    start = time.monotonic()
    sent = await message.answer("🏓 Checking...")
    latency = (time.monotonic() - start) * 1000

    await sent.edit_text(
        f"🏓 **PONG!**\n\n"
        f"⚡ Response: {latency:.0f} ms\n"
        f"🤖 Bot: Online"
    )


@router.message(Command("status"))
async def status(message: Message):
    uptime = int(time.monotonic() - START_TIME)
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)

    await message.answer(
        f"📊 **{BOT_NAME} STATUS**\n\n"
        f"🟢 Bot: Online\n"
        f"⏱ Uptime: {hours}h {minutes}m {seconds}s\n"
        f"🤖 AI: {'Configured' if AI_API_KEY else 'Not configured'}\n"
        f"👑 Owner ID: {'Configured' if OWNER_ID else 'Not configured'}"
    )


@router.message(Command("owner"))
async def owner(message: Message):
    if not OWNER_ID:
        return await message.answer("Owner ID abhi configure nahi hai.")

    await message.answer(
        f"👑 Bot owner ID: `{OWNER_ID}`"
    )
