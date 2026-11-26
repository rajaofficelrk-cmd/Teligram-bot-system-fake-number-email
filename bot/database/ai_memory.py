
import aiosqlite
from bot.config import DATABASE_PATH


async def init_ai_memory():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_memory_user
            ON ai_memory(user_id, id)
        """)
        await db.commit()


async def save_ai_message(user_id: int, role: str, content: str):
    if role not in ("user", "assistant"):
        raise ValueError("Invalid AI role")

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO ai_memory (user_id, role, content)
            VALUES (?, ?, ?)
        """, (user_id, role, content))

        await db.execute("""
            DELETE FROM ai_memory
            WHERE user_id = ?
            AND id NOT IN (
                SELECT id FROM ai_memory
                WHERE user_id = ?
                ORDER BY id DESC LIMIT 20
            )
        """, (user_id, user_id))

        await db.commit()


async def get_ai_memory(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT role, content FROM ai_memory
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 20
        """, (user_id,))
        rows = await cursor.fetchall()
        await cursor.close()

    rows.reverse()
    return [{"role": role, "content": content} for role, content in rows]


async def clear_ai_memory(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM ai_memory WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
