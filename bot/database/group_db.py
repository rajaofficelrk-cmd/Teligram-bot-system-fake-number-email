
import aiosqlite

from bot.config import DATABASE_PATH


async def init_group_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_settings (
                chat_id INTEGER PRIMARY KEY,
                saved_title TEXT,
                title_lock INTEGER DEFAULT 0,
                anti_link INTEGER DEFAULT 0,
                anti_flood INTEGER DEFAULT 1,
                welcome INTEGER DEFAULT 1,
                rules TEXT DEFAULT ''
            )
        """)
        await db.commit()


async def get_group(chat_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM group_settings WHERE chat_id = ?",
            (chat_id,)
        )
        row = await cursor.fetchone()
        await cursor.close()
        return row


async def update_group(chat_id, **settings):
    allowed = {
        "saved_title", "title_lock", "anti_link",
        "anti_flood", "welcome", "rules"
    }

    fields = {
        key: value for key, value in settings.items()
        if key in allowed
    }

    if not fields:
        return

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)",
            (chat_id,)
        )

        columns = ", ".join(
            f"{key} = ?" for key in fields
        )
        values = list(fields.values()) + [chat_id]

        await db.execute(
            f"UPDATE group_settings SET {columns} WHERE chat_id = ?",
            values
        )
        await db.commit()
