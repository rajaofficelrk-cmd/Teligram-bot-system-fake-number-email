
import re
import hashlib
import secrets
import string
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="text_tools")


@router.message(Command("reverse"))
async def reverse_text(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /reverse Hello Raja")
    await message.answer(text[::-1])


@router.message(Command("uppercase"))
async def uppercase(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /uppercase hello raja")
    await message.answer(text.upper())


@router.message(Command("lowercase"))
async def lowercase(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /lowercase HELLO RAJA")
    await message.answer(text.lower())


@router.message(Command("titlecase"))
async def titlecase(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /titlecase hello raja")
    await message.answer(text.title())


@router.message(Command("count"))
async def count_text(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /count Your text here")
    words = len(text.split())
    chars = len(text)
    lines = len(text.splitlines())
    await message.answer(
        f"📊 Characters: {chars}\n"
        f"📝 Words: {words}\n"
        f"📄 Lines: {lines}"
    )


@router.message(Command("sha256"))
async def sha256(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text:
        return await message.reply("Usage: /sha256 Your text")
    digest = hashlib.sha256(text.encode()).hexdigest()
    await message.answer(f"`{digest}`")


@router.message(Command("password"))
async def password(message: Message):
    parts = (message.text or "").split()
    length = 16

    if len(parts) > 1:
        if not parts[1].isdigit():
            return await message.reply("Usage: /password 16")
        length = int(parts[1])

    if not 8 <= length <= 64:
        return await message.reply("Length 8 se 64 ke beech rakho.")

    alphabet = string.ascii_letters + string.digits + "!@#$%&*?"
    result = "".join(secrets.choice(alphabet) for _ in range(length))
    await message.answer(f"🔐 Generated password:\n`{result}`")


@router.message(Command("username"))
async def username(message: Message):
    parts = (message.text or "").split()
    length = 10

    if len(parts) > 1 and parts[1].isdigit():
        length = max(5, min(20, int(parts[1])))

    alphabet = string.ascii_lowercase + string.digits
    result = "".join(secrets.choice(alphabet) for _ in range(length))
    await message.answer(f"👤 Username idea: `{result}`")


@router.message(Command("clean"))
async def clean_text(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /clean Your text")

    result = re.sub(r"\s+", " ", text).strip()
    await message.answer(result)


@router.message(Command("bold"))
async def bold_text(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /bold RK RAJA")
    await message.answer(f"<b>{text}</b>")


@router.message(Command("italic"))
async def italic_text(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /italic RK RAJA")
    await message.answer(f"<i>{text}</i>")


@router.message(Command("code"))
async def code_text(message: Message):
    text = (message.text or "").partition(" ")[2]
    if not text.strip():
        return await message.reply("Usage: /code print('Hello')")
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    await message.answer(f"<code>{safe}</code>")
