
import aiosqlite
from bot.config import DATABASE_PATH


async def init_profile_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                display_name TEXT DEFAULT '',
                bio TEXT DEFAULT '',
                message_count INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def ensure_profile(user_id: int, name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO user_profiles (user_id, display_name)
            VALUES (?, ?)
        """, (user_id, name))
        await db.commit()


async def update_bio(user_id: int, bio: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE user_profiles SET bio = ? WHERE user_id = ?
        """, (bio, user_id))
        await db.commit()


async def update_name(user_id: int, name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE user_profiles SET display_name = ? WHERE user_id = ?
        """, (name, user_id))
        await db.commit()


async def add_activity(user_id: int, name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO user_profiles (user_id, display_name, message_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                message_count = message_count + 1
        """, (user_id, name))
        await db.commit()


async def get_profile(user_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, display_name, bio, message_count, joined_at
            FROM user_profiles WHERE user_id = ?
        """, (user_id,))
        row = await cursor.fetchone()
        await cursor.close()
        return row


async def get_top_users(limit: int = 10):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT display_name, message_count
            FROM user_profiles
            ORDER BY message_count DESC
            LIMIT ?
        """, (limit,))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows
