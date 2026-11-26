
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN, BOT_NAME, LOG_LEVEL

from bot.database.db import init_db
from bot.database.group_db import init_group_db
from bot.database.notes_db import init_notes_db
from bot.database.profile_db import init_profile_db
from bot.database.tasks_db import init_tasks_db
from bot.database.ai_memory import init_ai_memory

from bot.handlers import (
    core,
    admin,
    tools,
    groups,
    group_settings,
    notes,
    profile,
    games,
    fun,
    text_tools,
    generators,
    tasks,
    help_menu,
    status,
    ai_chat
)

from bot.handlers.tasks import reminder_worker


def get_router(module, *names):
    for name in names:
        value = getattr(module, name, None)
        if value is not None:
            return value

    raise RuntimeError(
        f"Router not found in {module.__name__}"
    )


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing!")

    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    logging.info("Starting %s...", BOT_NAME)

    # Initialize databases
    await init_db()
    await init_group_db()
    await init_notes_db()
    await init_profile_db()
    await init_tasks_db()
    await init_ai_memory()

    # Create bot
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    # Register feature routers
    routers = [
        get_router(admin, "router", "admin_router"),
        get_router(groups, "router", "groups_router"),
        get_router(group_settings, "router", "settings_router"),
        get_router(notes, "router", "notes_router"),
        get_router(games, "router", "games_router"),
        get_router(fun, "router", "fun_router"),
        get_router(text_tools, "router", "text_tools_router"),
        get_router(generators, "router", "generators_router"),
        get_router(tasks, "router", "tasks_router"),
        get_router(help_menu, "router", "help_router"),
        get_router(status, "router", "status_router"),
        get_router(tools, "router", "tools_router"),
        get_router(ai_chat, "router", "ai_chat_router"),
        get_router(core, "router", "core_router"),
        get_router(profile, "router", "profile_router"),
    ]

    for item in routers:
        dp.include_router(item)

    # Start reminder worker
    worker = asyncio.create_task(reminder_worker(bot))

    try:
        await bot.delete_webhook(drop_pending_updates=True)

        logging.info("%s is online!", BOT_NAME)

        await dp.start_polling(bot)

    finally:
        worker.cancel()

        try:
            await worker
        except asyncio.CancelledError:
            pass

        await bot.session.close()
        logging.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
