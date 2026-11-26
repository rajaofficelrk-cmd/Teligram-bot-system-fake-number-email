import os
import aiosqlite
from bot.config import DATABASE_PATH

async def init_db():
    folder = os.path.dirname(DATABASE_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript('''
        CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, joined_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS groups(chat_id INTEGER PRIMARY KEY, title TEXT, saved_title TEXT, title_lock INTEGER DEFAULT 0, antilink INTEGER DEFAULT 0, antiflood INTEGER DEFAULT 0, welcome INTEGER DEFAULT 0, welcome_text TEXT DEFAULT 'Welcome {name}!');
        CREATE TABLE IF NOT EXISTS warnings(chat_id INTEGER, user_id INTEGER, count INTEGER DEFAULT 0, PRIMARY KEY(chat_id,user_id));
        CREATE TABLE IF NOT EXISTS notes(chat_id INTEGER, name TEXT, value TEXT, PRIMARY KEY(chat_id,name));
        CREATE TABLE IF NOT EXISTS settings(chat_id INTEGER, key TEXT, value TEXT, PRIMARY KEY(chat_id,key));
        ''')
        await db.commit()

async def execute(query, args=()):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(query, args)
        await db.commit()
        return cur

async def fetchone(query, args=()):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(query, args)
        return await cur.fetchone()

async def fetchall(query, args=()):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(query, args)
        return await cur.fetchall()

async def touch_user(user):
    await execute('INSERT INTO users(user_id,username,first_name) VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name', (user.id, user.username or '', user.first_name or ''))

async def ensure_group(chat):
    await execute('INSERT OR IGNORE INTO groups(chat_id,title,saved_title) VALUES(?,?,?)', (chat.id, chat.title or '', chat.title or ''))

async def group(chat_id):
    return await fetchone('SELECT chat_id,title,saved_title,title_lock,antilink,antiflood,welcome,welcome_text FROM groups WHERE chat_id=?', (chat_id,))

async def set_group_field(chat_id, field, value):
    allowed = {'title','saved_title','title_lock','antilink','antiflood','welcome','welcome_text'}
    if field not in allowed:
        raise ValueError('Invalid group field')
    await execute(f'UPDATE groups SET {field}=? WHERE chat_id=?', (value, chat_id))

async def get_setting(chat_id, key, default=''):
    row = await fetchone('SELECT value FROM settings WHERE chat_id=? AND key=?', (chat_id,key))
    return row[0] if row else default

async def set_setting(chat_id, key, value):
    await execute('INSERT INTO settings(chat_id,key,value) VALUES(?,?,?) ON CONFLICT(chat_id,key) DO UPDATE SET value=excluded.value', (chat_id,key,str(value)))
