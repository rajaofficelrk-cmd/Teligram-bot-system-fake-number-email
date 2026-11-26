
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from bot.database.group_db import (
    get_group,
    update_group
)

router = Router()


async def check_admin(message: Message):
    if not message.from_user:
        return False

    try:
        member = await message.bot.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in ("creator", "administrator")
    except Exception:
        return False


async def bot_can_change_info(message: Message):
    try:
        member = await message.bot.get_chat_member(
            message.chat.id,
            message.bot.id
        )
        return (
            member.status == "creator"
            or (
                member.status == "administrator"
                and member.can_change_info
            )
        )
    except Exception:
        return False


@router.message(Command("gclock"))
async def lock_title(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return await message.answer("Ye command sirf groups mein hai.")

    if not await check_admin(message):
        return await message.answer("Admin permission required.")

    if not await bot_can_change_info(message):
        return await message.answer(
            "Bot ko Change Group Info permission do."
        )

    await update_group(
        message.chat.id,
        saved_title=message.chat.title or "",
        title_lock=1
    )

    await message.answer(
        "🔒 Group title lock enabled.\n"
        "Bot title changes ko restore karne ki koshish karega."
    )


@router.message(Command("gcunlock"))
async def unlock_title(message: Message):
    if not await check_admin(message):
        return await message.answer("Admin permission required.")

    await update_group(
        message.chat.id,
        title_lock=0
    )

    await message.answer("🔓 Group title lock disabled.")


@router.message(Command("setgclock"))
async def set_locked_title(message: Message):
    if not await check_admin(message):
        return await message.answer("Admin permission required.")

    title = (message.text or "").partition(" ")[2].strip()

    if not title:
        return await message.answer(
            "Usage: /setgclock New Group Name"
        )

    if len(title) > 128:
        return await message.answer("Title too long.")

    if not await bot_can_change_info(message):
        return await message.answer(
            "Bot ko Change Group Info permission do."
        )

    try:
        await message.bot.set_chat_title(
            message.chat.id,
            title
        )

        await update_group(
            message.chat.id,
            saved_title=title,
            title_lock=1
        )

        await message.answer(
            f"🔒 Locked group title:\n{title}"
        )

    except TelegramBadRequest:
        await message.answer("Group title update nahi ho paya.")


@router.message(Command("lockstatus"))
async def lock_status(message: Message):
    data = await get_group(message.chat.id)

    if not data:
        return await message.answer("Group settings not found.")

    title_lock = bool(data[2])

    await message.answer(
        f"🔒 Title lock: {'ON' if title_lock else 'OFF'}\n"
        f"📌 Saved title: {data[1] or 'Not set'}"
    )


@router.chat_member()
async def restore_title(event):
    # Telegram chat_member updates do not report title changes.
    # Actual title restoration is handled by chat title updates below.
    pass


@router.message(F.new_chat_title)
async def title_changed(message: Message):
    data = await get_group(message.chat.id)

    if not data or not data[2]:
        return

    saved_title = data[1]

    if not saved_title or message.new_chat_title == saved_title:
        return

    if not await bot_can_change_info(message):
        return

    try:
        await message.bot.set_chat_title(
            message.chat.id,
            saved_title
        )
        await message.answer(
            "🔒 Group title lock active. Previous title restored."
        )
    except TelegramBadRequest:
        await message.answer(
            "Title restore nahi ho paya. Bot permission check karo."
        )
