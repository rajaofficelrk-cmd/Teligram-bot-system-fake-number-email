import asyncio, logging, sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.config import BOT_TOKEN
from bot.database.db import init_db
from bot.handlers import core, groups

async def main():
    if not BOT_TOKEN or BOT_TOKEN == 'PASTE_BOT_TOKEN_HERE':
        raise RuntimeError('BOT_TOKEN missing. .env file mein BotFather token set karo.')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    await init_db()
    bot=Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp=Dispatcher()
    dp.include_router(core.router)
    dp.include_router(groups.router)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__=='__main__':
    try: asyncio.run(main())
    except (KeyboardInterrupt,SystemExit): pass
