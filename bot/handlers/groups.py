
import re
import time
from collections import defaultdict, deque

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions
from aiogram.exceptions import TelegramBadRequest

router = Router()

FLOOD_LIMIT = 5
FLOOD_WINDOW = 8
user_messages = defaultdict(deque)
warnings = defaultdict(int)
group_rules = {}


async def is_admin(message: Message) -> bool:
    try:
        member = await message.bot.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in ("creator", "administrator")
    except Exception:
        return False


async def is_bot_admin(message: Message) -> bool:
    try:
        member = await message.bot.get_chat_member(
            message.chat.id,
            message.bot.id
        )
        return member.status in ("creator", "administrator")
    except Exception:
        return False


@router.message(F.new_chat_members)
async def welcome_members(message: Message):
    for member in message.new_chat_members:
        if member.id == message.bot.id:
            continue

        await message.answer(
            f"👋 Welcome {member.full_name}!\n"
            f"Welcome to {message.chat.title}.\n"
            "Enjoy your stay! ❤️"
        )


@router.message(Command("rules"))
async def show_rules(message: Message):
    rules = group_rules.get(
        message.chat.id,
        "Group rules abhi set nahi hain."
    )
    await message.answer(f"📜 GROUP RULES\n\n{rules}")


@router.message(Command("setrules"))
async def set_rules(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    rules = (message.text or "").partition(" ")[2].strip()

    if not rules:
        return await message.answer(
            "Usage: /setrules Be respectful."
        )

    group_rules[message.chat.id] = rules
    await message.answer("✅ Group rules updated.")


@router.message(Command("warn"))
async def warn_user(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not message.reply_to_message:
        return await message.answer(
            "Jis user ko warn karna hai uske message par reply karo."
        )

    target = message.reply_to_message.from_user

    if not target:
        return

    key = (message.chat.id, target.id)
    warnings[key] += 1

    await message.answer(
        f"⚠️ {target.full_name} warned.\n"
        f"Warnings: {warnings[key]}/3"
    )

    if warnings[key] >= 3:
        if not await is_bot_admin(message):
            return await message.answer(
                "Bot ko admin permission chahiye."
            )

        try:
            await message.bot.ban_chat_member(
                message.chat.id,
                target.id
            )
            warnings[key] = 0
            await message.answer("User removed after 3 warnings.")
        except TelegramBadRequest:
            await message.answer("User ko remove nahi kar paya.")


@router.message(Command("resetwarn"))
async def reset_warn(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not message.reply_to_message:
        return await message.answer("Reply to a user's message.")

    target = message.reply_to_message.from_user

    if target:
        warnings[(message.chat.id, target.id)] = 0
        await message.answer("✅ Warnings reset.")


@router.message(Command("mute"))
async def mute_user(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not message.reply_to_message:
        return await message.answer("Reply to the user to mute.")

    if not await is_bot_admin(message):
        return await message.answer("Bot ko admin permission do.")

    target = message.reply_to_message.from_user

    if not target:
        return

    try:
        await message.bot.restrict_chat_member(
            message.chat.id,
            target.id,
            ChatPermissions(can_send_messages=False)
        )
        await message.answer(f"🔇 {target.full_name} muted.")
    except TelegramBadRequest:
        await message.answer("Mute nahi ho paya.")


@router.message(Command("unmute"))
async def unmute_user(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not message.reply_to_message:
        return await message.answer("Reply to the muted user.")

    if not await is_bot_admin(message):
        return await message.answer("Bot ko admin permission do.")

    target = message.reply_to_message.from_user

    if not target:
        return

    try:
        await message.bot.restrict_chat_member(
            message.chat.id,
            target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await message.answer(f"🔊 {target.full_name} unmuted.")
    except TelegramBadRequest:
        await message.answer("Unmute nahi ho paya.")


@router.message(Command("kick"))
async def kick_user(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not message.reply_to_message:
        return await message.answer("Reply to the user to kick.")

    if not await is_bot_admin(message):
        return await message.answer("Bot ko admin permission do.")

    target = message.reply_to_message.from_user

    if not target:
        return

    try:
        await message.bot.ban_chat_member(
            message.chat.id, target.id
        )
        await message.bot.unban_chat_member(
            message.chat.id, target.id
        )
        await message.answer(f"👢 {target.full_name} kicked.")
    except TelegramBadRequest:
        await message.answer("Kick nahi ho paya.")


@router.message(Command("ban"))
async def ban_user(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not message.reply_to_message:
        return await message.answer("Reply to the user to ban.")

    if not await is_bot_admin(message):
        return await message.answer("Bot ko admin permission do.")

    target = message.reply_to_message.from_user

    if not target:
        return

    try:
        await message.bot.ban_chat_member(
            message.chat.id, target.id
        )
        await message.answer(f"🚫 {target.full_name} banned.")
    except TelegramBadRequest:
        await message.answer("Ban nahi ho paya.")


@router.message(Command("unban"))
async def unban_user(message: Message):
    if not await is_admin(message):
        return await message.answer("Admin permission required.")

    if not await is_bot_admin(message):
        return await message.answer("Bot ko admin permission do.")

    args = (message.text or "").split(maxsplit=1)

    if len(args) != 2 or not args[1].isdigit():
        return await message.answer("Usage: /unban USER_ID")

    try:
        await message.bot.unban_chat_member(
            message.chat.id, int(args[1])
        )
        await message.answer("✅ User unbanned.")
    except TelegramBadRequest:
        await message.answer("Unban nahi ho paya.")


# Anti-link
@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def group_protection(message: Message):
    if not message.from_user or message.from_user.is_bot:
        return

    if await is_admin(message):
        return

    text = message.text or ""

    links = re.search(
        r"(https?://|www\.|t\.me/|telegram\.me/)",
        text,
        re.IGNORECASE
    )

    if links:
        if await is_bot_admin(message):
            try:
                await message.delete()
                await message.answer(
                    f"⚠️ {message.from_user.full_name}, "
                    "links are not allowed."
                )
            except TelegramBadRequest:
                pass
        return

    # Anti-flood
    key = (message.chat.id, message.from_user.id)
    now = time.monotonic()

    queue = user_messages[key]
    queue.append(now)

    while queue and now - queue[0] > FLOOD_WINDOW:
        queue.popleft()

    if len(queue) > FLOOD_LIMIT:
        if await is_bot_admin(message):
            try:
                await message.delete()
                await message.answer(
                    f"⚠️ {message.from_user.full_name}, "
                    "please slow down."
                )
            except TelegramBadRequest:
                pass

        queue.clear()
