
import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="games")

TRUTHS = [
    "Tumhara favourite game kaunsa hai?",
    "Tumhari favourite movie kaunsi hai?",
    "Tumhara sabse bada gaming goal kya hai?",
    "Tumhe coding pasand hai ya gaming?"
]

DARES = [
    "Group mein kisi ek member ki achhi quality batao.",
    "Apne favourite game ka naam batao.",
    "Ek funny emoji bhejo.",
    "Apna favourite song ka naam batao."
]

JOKES = [
    "Programmer ka favourite place? Java cafe! 😂",
    "Computer thanda kyun tha? Kyunki uske paas Windows the! 😂",
    "Keyboard ne computer se kaha: Tum mere type ke ho! 😂"
]

QUESTIONS = [
    {
        "q": "Python mein list banane ke liye kya use hota hai?",
        "options": ["{}", "[]", "()", "<>"],
        "answer": 2
    },
    {
        "q": "HTML ka full form kya hai?",
        "options": [
            "Hyper Text Markup Language",
            "High Text Machine Language",
            "Home Tool Markup Language",
            "Hyper Transfer Main Link"
        ],
        "answer": 1
    },
    {
        "q": "2 + 8 × 2 = ?",
        "options": ["20", "18", "16", "12"],
        "answer": 2
    }
]

GUESS_GAMES = {}


@router.message(Command("rps"))
async def rps(message: Message):
    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2:
        return await message.reply(
            "Usage: /rps rock\n"
            "Options: rock, paper, scissors"
        )

    user_choice = parts[1].lower()
    choices = ["rock", "paper", "scissors"]

    if user_choice not in choices:
        return await message.reply("Rock, paper ya scissors choose karo.")

    bot_choice = random.choice(choices)

    if user_choice == bot_choice:
        result = "🤝 Draw!"
    elif (
        (user_choice == "rock" and bot_choice == "scissors")
        or (user_choice == "paper" and bot_choice == "rock")
        or (user_choice == "scissors" and bot_choice == "paper")
    ):
        result = "🏆 Tum jeet gaye!"
    else:
        result = "🤖 Bot jeet gaya!"

    await message.answer(
        f"🎮 Tum: {user_choice}\n"
        f"🤖 Bot: {bot_choice}\n\n{result}"
    )


@router.message(Command("guess"))
async def guess_start(message: Message):
    number = random.randint(1, 20)
    GUESS_GAMES[(message.chat.id, message.from_user.id)] = number

    await message.answer(
        "🎯 Number Guess Game!\n"
        "Maine 1 se 20 ke beech number socha hai.\n"
        "Guess bhejo: /answer 10"
    )


@router.message(Command("answer"))
async def guess_answer(message: Message):
    if not message.from_user:
        return

    key = (message.chat.id, message.from_user.id)
    target = GUESS_GAMES.get(key)

    if target is None:
        return await message.reply("Pehle /guess start karo.")

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply("Usage: /answer 10")

    number = int(parts[1])

    if not 1 <= number <= 20:
        return await message.reply("1 se 20 ke beech number bhejo.")

    if number == target:
        del GUESS_GAMES[key]
        await message.answer("🎉 Correct! Tum jeet gaye. /guess se dobara khelo.")
    elif number < target:
        await message.answer("📈 Thoda bada number try karo.")
    else:
        await message.answer("📉 Thoda chhota number try karo.")


@router.message(Command("quiz"))
async def quiz(message: Message):
    item = random.choice(QUESTIONS)

    GUESS_GAMES[("quiz", message.chat.id, message.from_user.id)] = item["answer"]

    options = "\n".join(
        f"{i}. {option}"
        for i, option in enumerate(item["options"], start=1)
    )

    await message.answer(
        f"🧠 **QUIZ TIME**\n\n{item['q']}\n\n"
        f"{options}\n\n"
        "Answer: /quizanswer 1"
    )


@router.message(Command("quizanswer"))
async def quiz_answer(message: Message):
    if not message.from_user:
        return

    key = ("quiz", message.chat.id, message.from_user.id)
    correct = GUESS_GAMES.pop(key, None)

    if correct is None:
        return await message.reply("Pehle /quiz start karo.")

    parts = (message.text or "").split(maxsplit=1)

    if len(parts) < 2 or not parts[1].isdigit():
        GUESS_GAMES[key] = correct
        return await message.reply("Usage: /quizanswer 1")

    answer = int(parts[1])

    if answer == correct:
        await message.answer("🎉 Correct answer!")
    else:
        await message.answer(f"❌ Wrong! Correct option: {correct}")


@router.message(Command("truth"))
async def truth(message: Message):
    await message.answer("💬 TRUTH:\n" + random.choice(TRUTHS))


@router.message(Command("dare"))
async def dare(message: Message):
    await message.answer("🎯 DARE:\n" + random.choice(DARES))


@router.message(Command("joke"))
async def joke(message: Message):
    await message.answer(random.choice(JOKES))


@router.message(Command("8ball"))
async def eight_ball(message: Message):
    answers = [
        "Haan, bilkul!",
        "Mumkin hai.",
        "Abhi kehna mushkil hai.",
        "Dobara try karo.",
        "Aaj chance achha lag raha hai!"
    ]

    await message.answer("🎱 " + random.choice(answers))
