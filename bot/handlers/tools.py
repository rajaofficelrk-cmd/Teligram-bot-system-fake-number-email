
import ast
import operator
import random
import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression):
    if len(expression) > 100:
        raise ValueError("Expression too long")

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Only numbers allowed")
            return node.value

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)

            if op_type not in OPERATORS:
                raise ValueError("Operator not allowed")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if op_type is ast.Pow and abs(right) > 10:
                raise ValueError("Power limit exceeded")

            result = OPERATORS[op_type](left, right)

            if abs(result) > 10**100:
                raise ValueError("Result too large")

            return result

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)

            if op_type not in OPERATORS:
                raise ValueError("Operator not allowed")

            return OPERATORS[op_type](evaluate(node.operand))

        raise ValueError("Invalid expression")

    return evaluate(tree)


@router.message(Command("calc"))
async def calculate(message: Message):
    expression = (message.text or "").partition(" ")[2].strip()

    if not expression:
        return await message.answer(
            "🧮 Example: /calc 25*4+10"
        )

    try:
        result = safe_calculate(expression)
        await message.answer(f"🧮 Result: {result}")
    except ZeroDivisionError:
        await message.answer("Zero se divide nahi kar sakte.")
    except Exception:
        await message.answer("Invalid calculation.")


@router.message(Command("dice"))
async def dice(message: Message):
    await message.answer(
        f"🎲 Dice result: {random.randint(1, 6)}"
    )


@router.message(Command("coin"))
async def coin(message: Message):
    result = random.choice(["HEADS 🪙", "TAILS 🪙"])
    await message.answer(f"Coin result: {result}")


@router.message(Command("random"))
async def random_number(message: Message):
    args = (message.text or "").split()

    if len(args) != 3:
        return await message.answer(
            "Example: /random 1 100"
        )

    try:
        start = int(args[1])
        end = int(args[2])

        if start > end or end - start > 1_000_000:
            raise ValueError()

        await message.answer(
            f"🎯 Random number: {random.randint(start, end)}"
        )
    except ValueError:
        await message.answer("Valid range enter karo.")


@router.message(Command("ping"))
async def ping(message: Message):
    start = time.perf_counter()

    sent = await message.answer("🏓 Pong!")

    elapsed = (time.perf_counter() - start) * 1000

    await sent.edit_text(
        f"🏓 Pong!\nResponse time: {elapsed:.2f} ms"
    )


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "👑 RK RAJA ULTIMATE XWD\n\n"
        "🤖 AI:\n"
        "/ai - Ask AI\n"
        "/clearhistory - Clear AI memory\n\n"
        "👤 PROFILE:\n"
        "/id - Telegram ID\n"
        "/profile - Your profile\n"
        "/stats - Bot statistics\n\n"
        "🛠 TOOLS:\n"
        "/calc - Calculator\n"
        "/dice - Roll dice\n"
        "/coin - Toss coin\n"
        "/random - Random number\n"
        "/ping - Bot response time\n\n"
        "👑 OWNER:\n"
        "/owner - Owner panel"
    )
