
import aiosqlite
from bot.config import DATABASE_PATH


async def init_tasks_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reminder TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                sent INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def add_task(user_id: int, task: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO user_tasks (user_id, task) VALUES (?, ?)",
            (user_id, task)
        )
        await db.commit()
        return cursor.lastrowid


async def get_tasks(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT id, task, completed FROM user_tasks
            WHERE user_id = ? ORDER BY id DESC LIMIT 30
        """, (user_id,))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def complete_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            UPDATE user_tasks SET completed = 1
            WHERE user_id = ? AND id = ?
        """, (user_id, task_id))
        await db.commit()
        return cursor.rowcount > 0


async def delete_task(user_id: int, task_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            DELETE FROM user_tasks WHERE user_id = ? AND id = ?
        """, (user_id, task_id))
        await db.commit()
        return cursor.rowcount > 0


async def add_reminder(user_id: int, reminder: str, remind_at: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO user_reminders (user_id, reminder, remind_at)
            VALUES (?, ?, ?)
        """, (user_id, reminder, remind_at))
        await db.commit()
        return cursor.lastrowid


async def get_due_reminders(now: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT id, user_id, reminder
            FROM user_reminders
            WHERE sent = 0 AND remind_at <= ?
        """, (now,))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows


async def mark_reminder_sent(reminder_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE user_reminders SET sent = 1 WHERE id = ?
        """, (reminder_id,))
        await db.commit()
