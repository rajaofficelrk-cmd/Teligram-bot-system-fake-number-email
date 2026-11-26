
import aiosqlite
from bot.config import DATABASE_PATH


async def init_notes_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                note_name TEXT NOT NULL,
                note_text TEXT NOT NULL,
                UNIQUE(chat_id, note_name)
            )
        """)
        await db.commit()


async def save_note(chat_id: int, name: str, content: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO group_notes (chat_id, note_name, note_text)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id, note_name)
            DO UPDATE SET note_text = excluded.note_text
        """, (chat_id, name.lower(), content))
        await db.commit()


async def get_note(chat_id: int, name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT note_text FROM group_notes
            WHERE chat_id = ? AND note_name = ?
        """, (chat_id, name.lower()))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0] if row else None


async def list_notes(chat_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            SELECT note_name FROM group_notes
            WHERE chat_id = ?
            ORDER BY note_name
        """, (chat_id,))
        rows = await cursor.fetchall()
        await cursor.close()
        return [row[0] for row in rows]


async def delete_note(chat_id: int, name: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            DELETE FROM group_notes
            WHERE chat_id = ? AND note_name = ?
        """, (chat_id, name.lower()))
        await db.commit()
        return cursor.rowcount > 0
