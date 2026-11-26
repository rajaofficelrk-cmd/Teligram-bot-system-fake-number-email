
import os
import aiosqlite

from bot.config import DATABASE_PATH


async def init_db():
    folder = os.path.dirname(DATABASE_PATH)

    if folder:
        os.makedirs(folder, exist_ok=True)

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_user_chat
            ON chat_history(user_id, chat_id, id)
        """)

        await db.commit()


async def save_user(user_id, username=None, first_name=None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username, first_name))

        await db.commit()


async def add_message(user_id, chat_id, role, content):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO chat_history
            (user_id, chat_id, role, content)
            VALUES (?, ?, ?, ?)
        """, (user_id, chat_id, role, content))

        await db.execute("""
            DELETE FROM chat_history
            WHERE user_id = ? AND chat_id = ?
            AND id NOT IN (
                SELECT id FROM chat_history
                WHERE user_id = ? AND chat_id = ?
                ORDER BY id DESC LIMIT 20
            )
        """, (user_id, chat_id, user_id, chat_id))

        await db.commit()


async def get_history(user_id, chat_id, limit=10):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT role, content
            FROM chat_history
            WHERE user_id = ? AND chat_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, chat_id, limit))

        rows = await cursor.fetchall()
        await cursor.close()

    rows.reverse()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


async def clear_history(user_id, chat_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            DELETE FROM chat_history
            WHERE user_id = ? AND chat_id = ?
        """, (user_id, chat_id))

        await db.commit()


async def get_stats():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users"
        )
        users = (await cursor.fetchone())[0]
        await cursor.close()

        cursor = await db.execute(
            "SELECT COUNT(*) FROM chat_history"
        )
        messages = (await cursor.fetchone())[0]
        await cursor.close()

    return {
        "users": users,
        "messages": messages
    }
