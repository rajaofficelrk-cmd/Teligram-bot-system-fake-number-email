
import random
import string

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="generators")


@router.message(Command("nickname"))
async def nickname(message: Message):
    first = ["Dark", "Royal", "Silent", "Crazy", "Legend", "Shadow", "Ultra"]
    second = ["Raja", "Hunter", "Player", "King", "Dev", "Warrior", "XWD"]
    await message.answer(
        "✨ Nickname: " + random.choice(first) + random.choice(second)
    )


@router.message(Command("teamname"))
async def teamname(message: Message):
    first = ["Night", "Royal", "Cyber", "Alpha", "Elite", "Nova"]
    second = ["Legends", "Squad", "Riders", "Storm", "Force", "Crew"]
    await message.answer(
        "🏆 Team Name: " + random.choice(first) + random.choice(second)
    )


@router.message(Command("bio"))
async def bio(message: Message):
    ideas = [
        "Learning every day 🚀 | Building my future",
        "Gaming • Coding • Creativity ✨",
        "Dream big. Work smart. Stay humble.",
        "Official vibes | Positive energy 👑",
        "Creating something new every day 💻"
    ]
    await message.answer("📝 Bio idea:\n" + random.choice(ideas))


@router.message(Command("quote"))
async def quote(message: Message):
    quotes = [
        "Small steps every day create big changes.",
        "Consistency is more powerful than motivation.",
        "Learn from yesterday and build tomorrow.",
        "Your ideas become real when you work on them."
    ]
    await message.answer("💡 " + random.choice(quotes))


@router.message(Command("emoji"))
async def emoji(message: Message):
    sets = [
        "🔥 👑 ⚡ 🚀 💻",
        "❤️ ✨ 🌟 😊 🎉",
        "🎮 🏆 🎯 🕹️ 👾",
        "🌈 🦋 🌸 🌻 💫"
    ]
    await message.answer(random.choice(sets))


@router.message(Command("number"))
async def number(message: Message):
    await message.answer(
        "🔢 Random ID idea: "
        + "".join(random.choices(string.digits, k=8))
    )


@router.message(Command("stylish"))
async def stylish(message: Message):
    text = (message.text or "").partition(" ")[2].strip()
    if not text:
        return await message.reply("Usage: /stylish RK RAJA")

    styles = [
        lambda s: s.upper(),
        lambda s: s.lower(),
        lambda s: " ".join(f"【{c}】" for c in s),
        lambda s: "亗 " + s + " 亗",
        lambda s: "『" + s + "』",
        lambda s: "꧁༺ " + s + " ༻꧂"
    ]

    await message.answer(random.choice(styles)(text))


@router.message(Command("fakechat"))
async def fakechat(message: Message):
    await message.answer(
        "💬 Fake chat text template:\n\n"
        "Person 1: Hello!\n"
        "Person 2: Hi, what's up?\n"
        "Person 1: All good! 😊\n\n"
        "Ye sirf fictional chat template hai."
    )
