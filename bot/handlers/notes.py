
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.notes_db import (
    save_note,
    get_note,
    list_notes,
    delete_note
)

router = Router(name="notes")


async def is_admin(message: Message):
    if not message.from_user:
        return False
    try:
        member = await message.bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        return member.status in ("creator", "administrator")
    except Exception:
        return False


@router.message(Command("save"))
async def save_command(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return await message.reply("❌ Ye command group mein use karo.")

    if not await is_admin(message):
        return await message.reply("❌ Sirf group admins notes save kar sakte hain.")

    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply(
            "Usage:\n/save note_name Note ka text"
        )

    name, content = parts[1].strip(), parts[2].strip()

    if not name or not content or len(name) > 50:
        return await message.reply("❌ Note name ya text valid nahi hai.")

    await save_note(message.chat.id, name, content)
    await message.reply(f"✅ Note '{name}' save ho gaya.")


@router.message(Command("get"))
async def get_command(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Usage: /get note_name")

    name = parts[1].strip()
    content = await get_note(message.chat.id, name)

    if content is None:
        return await message.reply("❌ Ye note nahi mila.")

    await message.answer(
        f"📌 **{name}**\n\n{content}"
    )


@router.message(Command("notes"))
async def notes_command(message: Message):
    notes = await list_notes(message.chat.id)

    if not notes:
        return await message.reply("📭 Is group mein koi saved note nahi hai.")

    output = "\n".join(f"• {name}" for name in notes)
    await message.answer(f"📚 **Saved Notes**\n\n{output}")


@router.message(Command("clear"))
async def clear_command(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return await message.reply("❌ Ye command group mein use karo.")

    if not await is_admin(message):
        return await message.reply("❌ Sirf group admins notes delete kar sakte hain.")

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Usage: /clear note_name")

    name = parts[1].strip()
    deleted = await delete_note(message.chat.id, name)

    if deleted:
        await message.reply(f"🗑 Note '{name}' delete ho gaya.")
    else:
        await message.reply("❌ Ye note nahi mila.")
