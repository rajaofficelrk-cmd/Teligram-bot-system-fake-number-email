
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import TIMEZONE
from bot.database.tasks_db import (
    add_task,
    get_tasks,
    complete_task,
    delete_task,
    add_reminder,
    get_due_reminders,
    mark_reminder_sent
)

router = Router(name="tasks")
TZ = ZoneInfo(TIMEZONE)


@router.message(Command("addtask"))
async def addtask(message: Message):
    if not message.from_user:
        return

    task = (message.text or "").partition(" ")[2].strip()
    if not task:
        return await message.reply("Usage: /addtask Homework complete")

    if len(task) > 300:
        return await message.reply("Task maximum 300 characters ka ho sakta hai.")

    task_id = await add_task(message.from_user.id, task)
    await message.answer(f"✅ Task added. ID: {task_id}")


@router.message(Command("mytasks"))
async def mytasks(message: Message):
    if not message.from_user:
        return

    rows = await get_tasks(message.from_user.id)
    if not rows:
        return await message.reply("📭 Abhi koi task nahi hai.")

    lines = []
    for task_id, task, completed in rows:
        status = "✅" if completed else "⏳"
        lines.append(f"{status} #{task_id} — {task}")

    await message.answer("📋 **YOUR TASKS**\n\n" + "\n".join(lines))


@router.message(Command("done"))
async def done(message: Message):
    if not message.from_user:
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply("Usage: /done 1")

    success = await complete_task(message.from_user.id, int(parts[1]))
    await message.answer("✅ Task completed." if success else "❌ Task nahi mila.")


@router.message(Command("deltask"))
async def deltask(message: Message):
    if not message.from_user:
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        return await message.reply("Usage: /deltask 1")

    success = await delete_task(message.from_user.id, int(parts[1]))
    await message.answer("🗑 Task deleted." if success else "❌ Task nahi mila.")


@router.message(Command("remind"))
async def remind(message: Message):
    if not message.from_user:
        return

    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply(
            "Usage: /remind 10m Meeting\n"
            "Formats: 10m, 2h, 1d"
        )

    amount_text, reminder = parts[1], parts[2]
    unit = amount_text[-1:].lower()
    number_text = amount_text[:-1]

    if not number_text.isdigit() or int(number_text) <= 0:
        return await message.reply("Time format sahi nahi hai.")

    amount = int(number_text)
    multipliers = {"m": 60, "h": 3600, "d": 86400}

    if unit not in multipliers:
        return await message.reply("Use m, h ya d. Example: /remind 10m Meeting")

    if amount > 30 and unit == "d":
        return await message.reply("Reminder maximum 30 days tak set kar sakte ho.")

    remind_at = datetime.now(TZ) + timedelta(seconds=amount * multipliers[unit])
    await add_reminder(
        message.from_user.id,
        reminder,
        remind_at.isoformat()
    )

    await message.answer(
        "⏰ Reminder saved!\n"
        f"Message: {reminder}\n"
        f"Time: {remind_at.strftime('%d-%m-%Y %I:%M %p')}"
    )


async def reminder_worker(bot):
    while True:
        now = datetime.now(TZ).isoformat()
        reminders = await get_due_reminders(now)

        for reminder_id, user_id, reminder in reminders:
            try:
                await bot.send_message(
                    user_id,
                    f"⏰ **REMINDER**\n\n{reminder}"
                )
                await mark_reminder_sent(reminder_id)
            except Exception:
                # Keep it pending if delivery fails.
                pass

        await asyncio.sleep(15)
