
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.services.ai import ask_ai
from bot.database.ai_memory import (
    save_ai_message,
    get_ai_memory,
    clear_ai_memory
)

router = Router(name="ai_chat")


@router.message(Command("aichat"))
async def ai_chat_command(message: Message):
    if not message.from_user:
        return

    prompt = (message.text or "").partition(" ")[2].strip()

    if not prompt:
        return await message.reply(
            "Usage: /aichat Hello, kaise ho?"
        )

    history = await get_ai_memory(message.from_user.id)

    await save_ai_message(message.from_user.id, "user", prompt)

    answer = await ask_ai(prompt, history=history)

    if not answer:
        answer = "AI se reply nahi mila."

    await save_ai_message(
        message.from_user.id, "assistant", answer
    )

    await message.answer(answer[:4000])


@router.message(Command("aiclear"))
async def ai_clear_command(message: Message):
    if not message.from_user:
        return

    await clear_ai_memory(message.from_user.id)
    await message.answer("🧹 AI conversation memory clear ho gayi.")


@router.message(Command("aistatus"))
async def ai_status_command(message: Message):
    from bot.config import AI_API_KEY, AI_MODEL

    await message.answer(
        "🤖 **AI STATUS**\n\n"
        f"API Key: {'Configured' if AI_API_KEY else 'Missing'}\n"
        f"Model: {AI_MODEL}"
    )
