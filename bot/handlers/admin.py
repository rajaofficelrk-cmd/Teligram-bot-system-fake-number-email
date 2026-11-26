
import aiosqlite

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import OWNER_ID, DATABASE_PATH
from bot.database.db import get_stats

router = Router()

maintenance_mode = False


def is_owner(message: Message) -> bool:
    return bool(
        message.from_user
        and OWNER_ID != 0
        and message.from_user.id == OWNER_ID
    )


@router.message(Command("owner"))
async def owner_panel(message: Message):
    if not is_owner(message):
        return await message.answer("⛔ Owner only command.")

    await message.answer(
        "👑 RK RAJA OWNER PANEL\n\n"
        "/botstats - Statistics\n"
        "/broadcast TEXT - Send announcement\n"
        "/maintenance on - Enable maintenance\n"
        "/maintenance off - Disable maintenance"
    )


@router.message(Command("botstats"))
async def bot_stats(message: Message):
    if not is_owner(message):
        return await message.answer("⛔ Owner only.")

    stats = await get_stats()

    await message.answer(
        "📊 BOT STATISTICS\n\n"
        f"👥 Users: {stats['users']}\n"
        f"💬 AI messages: {stats['messages']}\n"
        f"🔧 Maintenance: {maintenance_mode}"
    )


@router.message(Command("maintenance"))
async def maintenance(message: Message):
    global maintenance_mode

    if not is_owner(message):
        return await message.answer("⛔ Owner only.")

    args = (message.text or "").split(maxsplit=1)

    if len(args) != 2 or args[1].lower() not in ("on", "off"):
        return await message.answer(
            "Usage:\n/maintenance on\n/maintenance off"
        )

    maintenance_mode = args[1].lower() == "on"

    await message.answer(
        "🔧 Maintenance enabled."
        if maintenance_mode
        else "✅ Maintenance disabled."
    )


@router.message(Command("broadcast"))
async def broadcast(message: Message):
    if not is_owner(message):
        return await message.answer("⛔ Owner only.")

    text = (message.text or "").partition(" ")[2].strip()

    if not text:
        return await message.answer(
            "Usage: /broadcast Your announcement"
        )

    sent = 0
    failed = 0

    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        users = await cursor.fetchall()
        await cursor.close()

    await message.answer(
        f"📢 Broadcast starting for {len(users)} users."
    )

    for (user_id,) in users:
        try:
            await message.bot.send_message(user_id, text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        "📢 BROADCAST FINISHED\n\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}"
    )
