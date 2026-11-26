
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database.profile_db import (
    ensure_profile,
    update_bio,
    update_name,
    add_activity,
    get_profile,
    get_top_users
)

router = Router(name="profile")


@router.message(Command("profile"))
async def profile_command(message: Message):
    if not message.from_user:
        return

    user = message.from_user
    await ensure_profile(user.id, user.full_name)
    data = await get_profile(user.id)

    if not data:
        return await message.reply("Profile load nahi hua.")

    user_id, name, bio, count, joined = data

    await message.answer(
        "👤 **USER PROFILE**\n\n"
        f"🆔 ID: `{user_id}`\n"
        f"📛 Name: {name or user.full_name}\n"
        f"📝 Bio: {bio or 'Not set'}\n"
        f"💬 Messages: {count}\n"
        f"📅 Created: {joined}"
    )


@router.message(Command("setbio"))
async def setbio_command(message: Message):
    if not message.from_user:
        return

    bio = (message.text or "").partition(" ")[2].strip()

    if not bio:
        return await message.reply("Usage: /setbio Your bio")

    if len(bio) > 200:
        return await message.reply("❌ Bio maximum 200 characters ka ho sakta hai.")

    await ensure_profile(message.from_user.id, message.from_user.full_name)
    await update_bio(message.from_user.id, bio)

    await message.reply("✅ Bio update ho gaya.")


@router.message(Command("setname"))
async def setname_command(message: Message):
    if not message.from_user:
        return

    name = (message.text or "").partition(" ")[2].strip()

    if not name:
        return await message.reply("Usage: /setname Your display name")

    if len(name) > 40:
        return await message.reply("❌ Name maximum 40 characters ka ho sakta hai.")

    await ensure_profile(message.from_user.id, message.from_user.full_name)
    await update_name(message.from_user.id, name)

    await message.reply("✅ Display name update ho gaya.")


@router.message(Command("mystats"))
async def mystats_command(message: Message):
    if not message.from_user:
        return

    await ensure_profile(message.from_user.id, message.from_user.full_name)
    data = await get_profile(message.from_user.id)

    if not data:
        return await message.reply("Stats nahi mile.")

    await message.answer(
        f"📊 **YOUR STATS**\n\n"
        f"💬 Messages: {data[3]}\n"
        f"📅 Joined database: {data[4]}"
    )


@router.message(Command("topusers"))
async def topusers_command(message: Message):
    users = await get_top_users(10)

    if not users:
        return await message.reply("Abhi activity data nahi hai.")

    lines = [
        f"{index}. {name or 'User'} — {count} messages"
        for index, (name, count) in enumerate(users, start=1)
    ]

    await message.answer("🏆 **TOP ACTIVE USERS**\n\n" + "\n".join(lines))


@router.message()
async def track_activity(message: Message):
    if not message.from_user or message.from_user.is_bot:
        return

    await add_activity(
        message.from_user.id,
        message.from_user.full_name
    )
