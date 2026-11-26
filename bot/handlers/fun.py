
import random
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="fun")


@router.message(Command("coin"))
async def coin(message: Message):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await message.answer(f"🪙 Result: {result}")


@router.message(Command("dice"))
async def dice(message: Message):
    number = random.randint(1, 6)
    await message.answer(f"🎲 Dice result: {number}")


@router.message(Command("random"))
async def random_number(message: Message):
    parts = (message.text or "").split()

    if len(parts) != 3:
        return await message.reply("Usage: /random 1 100")

    if not parts[1].isdigit() or not parts[2].isdigit():
        return await message.reply("Dono values numbers honi chahiye.")

    start, end = int(parts[1]), int(parts[2])

    if start > end or end - start > 1000000:
        return await message.reply("Range valid rakho (maximum 10 lakh).")

    await message.answer(f"🎲 Random number: {random.randint(start, end)}")


@router.message(Command("flip"))
async def flip(message: Message):
    await message.answer(
        random.choice(["🙃 Upside down!", "🔄 Flip complete!"])
    )


@router.message(Command("choose"))
async def choose(message: Message):
    choices = (message.text or "").partition(" ")[2]
    items = [x.strip() for x in choices.split("|") if x.strip()]

    if len(items) < 2:
        return await message.reply(
            "Usage: /choose Cricket | Football | Gaming"
        )

    await message.answer("🤔 My choice: " + random.choice(items))


@router.message(Command("time"))
async def time_command(message: Message):
    now = datetime.now().astimezone()
    await message.answer(
        "🕒 Current server time:\n"
        + now.strftime("%d-%m-%Y %I:%M:%S %p %Z")
    )


@router.message(Command("love"))
async def love(message: Message):
    # Fun compatibility score; not a real measurement.
    score = random.randint(1, 100)
    await message.answer(
        f"💫 Fun compatibility score: {score}%\n"
        "Ye sirf entertainment ke liye random score hai."
    )


@router.message(Command("compliment"))
async def compliment(message: Message):
    lines = [
        "Tumhari creativity achhi hai! ✨",
        "Keep learning and keep growing! 🚀",
        "Tumhara confidence hi tumhari strength hai! 👑",
        "Aaj kuch naya seekhne ka din hai! 💡"
    ]
    await message.answer(random.choice(lines))
