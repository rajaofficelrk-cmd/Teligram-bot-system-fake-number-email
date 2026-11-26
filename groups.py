
import re
import time
from collections import defaultdict

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions

from bot.database.group_db import get_group, update_group

router = Router(name="groups")

_WARNINGS = defaultdict(int)
_LAST_MESSAGE = {}


async def is_admin(message: Message) -> bool:
    if not message.from_user:
        return False
    try:
        member = await message.bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        return member.status in ("creator", "administrator")
    except Exception:
        return False


async def group_row(chat_id: int):
    return await get_group(chat_id)


async def setting(chat_id: int, index: int, default=0):
    row = await group_row(chat_id)
    return row[index] if row else default


def reply_target(message: Message):
    if not message.reply_to_message:
        return None
    return message.reply_to_message.from_user


@router.message(Command("rules"))
async def show_rules(message: Message):
    row = await group_row(message.chat.id)
    rules = row[6] if row and row[6] else "Abhi group rules set nahi kiye gaye."
    await message.answer(f"📜 **Group Rules**\n\n{rules}")


@router.message(Command("setrules"))
async def set_rules(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Sirf group admins rules set kar sakte hain.")

    rules = (message.text or "").partition(" ")[2].strip()
    if not rules:
        return await message.reply("Usage: /setrules Rules yahan likho")

    await update_group(message.chat.id, rules=rules)
    await message.reply("✅ Group rules save ho gaye.")


@router.message(Command("antilink"))
async def anti_link_toggle(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    arg = (message.text or "").partition(" ")[2].strip().lower()
    if arg not in ("on", "off"):
        return await message.reply("Usage: /antilink on  ya  /antilink off")

    await update_group(message.chat.id, anti_link=int(arg == "on"))
    await message.reply(f"🔗 Anti-link {arg.upper()}.")


@router.message(Command("antiflood"))
async def anti_flood_toggle(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    arg = (message.text or "").partition(" ")[2].strip().lower()
    if arg not in ("on", "off"):
        return await message.reply("Usage: /antiflood on  ya  /antiflood off")

    await update_group(message.chat.id, anti_flood=int(arg == "on"))
    await message.reply(f"⚡ Anti-flood {arg.upper()}.")


@router.message(Command("welcome"))
async def welcome_toggle(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    arg = (message.text or "").partition(" ")[2].strip().lower()
    if arg not in ("on", "off"):
        return await message.reply("Usage: /welcome on  ya  /welcome off")

    await update_group(message.chat.id, welcome=int(arg == "on"))
    await message.reply(f"👋 Welcome messages {arg.upper()}.")


@router.message(Command("warn"))
async def warn_user(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    target = reply_target(message)
    if not target or target.is_bot:
        return await message.reply("Jis member ko warn karna hai uske message par reply karo.")

    _WARNINGS[(message.chat.id, target.id)] += 1
    count = _WARNINGS[(message.chat.id, target.id)]

    await message.reply(
        f"⚠️ {target.full_name} ko warning mili.\n"
        f"Warnings: {count}/3"
    )

    if count >= 3:
        try:
            await message.bot.ban_chat_member(message.chat.id, target.id)
            _WARNINGS[(message.chat.id, target.id)] = 0
            await message.answer(f"🚫 {target.full_name} ko 3 warnings ke baad group se ban kiya gaya.")
        except Exception:
            await message.answer("⚠️ 3 warnings ho gayi, lekin bot member ko ban nahi kar paya. Admin permissions check karo.")


@router.message(Command("resetwarn"))
async def reset_warn(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    target = reply_target(message)
    if not target:
        return await message.reply("Member ke message par reply karke /resetwarn bhejo.")

    _WARNINGS[(message.chat.id, target.id)] = 0
    await message.reply("✅ Member ki warnings reset ho gayi.")


@router.message(Command("mute"))
async def mute_user(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    target = reply_target(message)
    if not target or target.is_bot:
        return await message.reply("Member ke message par reply karke /mute bhejo.")

    try:
        await message.bot.restrict_chat_member(
            message.chat.id,
            target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.reply(f"🔇 {target.full_name} muted.")
    except Exception as exc:
        await message.reply(f"❌ Mute nahi hua. Bot admin permissions check karo. ({type(exc).__name__})")


@router.message(Command("unmute"))
async def unmute_user(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    target = reply_target(message)
    if not target:
        return await message.reply("Member ke message par reply karke /unmute bhejo.")

    try:
        await message.bot.restrict_chat_member(
            message.chat.id,
            target.id,
            permissions=ChatPermissions(
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
        await message.reply(f"🔊 {target.full_name} unmuted.")
    except Exception as exc:
        await message.reply(f"❌ Unmute nahi hua. ({type(exc).__name__})")


@router.message(Command("kick"))
async def kick_user(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    target = reply_target(message)
    if not target or target.is_bot:
        return await message.reply("Member ke message par reply karke /kick bhejo.")

    try:
        await message.bot.ban_chat_member(message.chat.id, target.id)
        await message.bot.unban_chat_member(
            message.chat.id, target.id, only_if_banned=True
        )
        await message.reply(f"👢 {target.full_name} ko group se remove kiya.")
    except Exception as exc:
        await message.reply(f"❌ Kick nahi hua. ({type(exc).__name__})")


@router.message(Command("ban"))
async def ban_user(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    target = reply_target(message)
    if not target or target.is_bot:
        return await message.reply("Member ke message par reply karke /ban bhejo.")

    try:
        await message.bot.ban_chat_member(message.chat.id, target.id)
        await message.reply(f"🚫 {target.full_name} banned.")
    except Exception as exc:
        await message.reply(f"❌ Ban nahi hua. ({type(exc).__name__})")


@router.message(Command("unban"))
async def unban_user(message: Message):
    if not await is_admin(message):
        return await message.reply("❌ Admin only command.")

    arg = (message.text or "").partition(" ")[2].strip()
    if not arg.lstrip("-").isdigit():
        return await message.reply("Usage: /unban USER_ID")

    try:
        await message.bot.unban_chat_member(
            message.chat.id, int(arg), only_if_banned=True
        )
        await message.reply("✅ User unbanned.")
    except Exception as exc:
        await message.reply(f"❌ Unban nahi hua. ({type(exc).__name__})")


@router.message(F.new_chat_members)
async def welcome_new_members(message: Message):
    enabled = await setting(message.chat.id, 5, 1)
    if not enabled:
        return

    for member in message.new_chat_members:
        if not member.is_bot:
            await message.answer(
                f"👋 Welcome {member.full_name}!\n"
                "Group mein aapka swagat hai. /rules padh lena."
            )


@router.message(F.text)
async def group_protection(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if not message.from_user or await is_admin(message):
        return

    row = await group_row(message.chat.id)
    anti_link = bool(row[3]) if row else False
    anti_flood = bool(row[4]) if row else True

    if anti_link and re.search(
        r"(https?://|www\.|t\.me/|telegram\.me/)",
        message.text or "",
        re.IGNORECASE
    ):
        try:
            await message.delete()
            await message.answer("🔗 Links allowed nahi hain.")
        except Exception:
            pass
        return

    if anti_flood:
        key = (message.chat.id, message.from_user.id)
        now = time.monotonic()
        previous = _LAST_MESSAGE.get(key, 0)

        if now - previous < 0.8:
            try:
                await message.delete()
            except Exception:
                pass
        _LAST_MESSAGE[key] = now
