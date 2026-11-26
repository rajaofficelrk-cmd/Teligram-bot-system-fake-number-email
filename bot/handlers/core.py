
import html

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import BOT_NAME
from bot.services.ai import ask_ai
from bot.database.ai_memory import (
    save_ai_message,
    get_ai_memory,
    clear_ai_memory
)

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    name = html.escape(message.from_user.first_name or "Friend")

    await message.answer(
        f"👑 <b>WELCOME TO {html.escape(BOT_NAME)}</b>\n\n"
        f"Hello {name}!\n\n"
        "Main tumhara RK RAJA AI Assistant hoon.\n\n"
        "💬 Mujhse normal chat kar sakte ho.\n"
        "🤖 /ai - AI se baat karo\n"
        "🧹 /clearhistory - Chat memory clear karo\n"
        "🆔 /id - Telegram ID dekho\n"
        "📚 /help - Commands dekho"
    )


@router.message(Command("id"))
async def id_command(message: Message):
    await message.answer(
        f"🆔 <b>Your ID:</b> <code>{message.from_user.id}</code>\n"
        f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>"
    )


@router.message(Command("ai"))
async def ai_command(message: Message):
    prompt = (message.text or "").partition(" ")[2].strip()

    if not prompt:
        await message.answer(
            "Example:\n"
            "<code>/ai Hello Raja, kaise ho?</code>"
        )
        return

    user_id = message.from_user.id
    history = await get_ai_memory(user_id)

    status = await message.answer("🤖 AI soch raha hai...")

    answer = await ask_ai(prompt, history)

    await save_ai_message(user_id, "user", prompt)
    await save_ai_message(user_id, "assistant", answer)

    await status.edit_text(
        html.escape(answer),
        parse_mode="HTML"
    )


@router.message(Command("clearhistory"))
async def clear_history_command(message: Message):
    await clear_ai_memory(message.from_user.id)

    await message.answer(
        "🧹 <b>AI memory clear ho gayi!</b>\n"
        "Ab nayi conversation shuru kar sakte ho."
    )


@router.message(
    F.chat.type == "private",
    F.text,
    ~F.text.startswith("/")
)
async def automatic_ai_chat(message: Message):
    user_id = message.from_user.id
    prompt = message.text.strip()

    if not prompt:
        return

    history = await get_ai_memory(user_id)

    status = await message.answer("💭 Reply taiyar kar raha hoon...")

    answer = await ask_ai(prompt, history)

    await save_ai_message(user_id, "user", prompt)
    await save_ai_message(user_id, "assistant", answer)

    await status.edit_text(
        html.escape(answer),
        parse_mode="HTML"
    )
