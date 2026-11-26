import random, string
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot.config import BOT_NAME, OWNER_ID
from bot.database.db import touch_user, fetchone, fetchall, execute
from bot.services.ai import ask_ai

router = Router()

@router.message(CommandStart())
async def start(m: Message):
    await touch_user(m.from_user)
    await m.answer(f'👑 <b>{BOT_NAME}</b>\n\nWelcome {m.from_user.first_name}!\n/help — commands\n/id — your Telegram ID', parse_mode='HTML')

@router.message(Command('help','menu'))
async def help_cmd(m: Message):
    await m.answer('''👑 <b>RK RAJA ULTIMATE XWD</b>

<b>Basic</b>
/start /help /menu /id /profile /stats /about

<b>Group</b>
/gclock /gcunlock /setgclock /lockstatus
/antilink on|off /antiflood on|off
/welcome on|off /setwelcome TEXT
/rules /setrules TEXT /note NAME TEXT /get NAME /notes

<b>Moderation</b>
/warn (reply) /warnings (reply) /clearwarns (reply)
/kick (reply) /ban (reply) /mute MINUTES (reply) /unmute (reply)
/del (reply) /pin (reply) /unpin

<b>Fun & tools</b>
/coin /dice /roll MAX /password /upper TEXT /lower TEXT /reverse TEXT /count TEXT
/ai TEXT (optional AI API required)

<b>Owner</b>
/broadcast TEXT''', parse_mode='HTML')

@router.message(Command('id'))
async def id_cmd(m: Message):
    await m.answer(f'Your ID: <code>{m.from_user.id}</code>\nChat ID: <code>{m.chat.id}</code>', parse_mode='HTML')

@router.message(Command('about'))
async def about(m: Message):
    await m.answer(f'🤖 {BOT_NAME}\nPython • aiogram 3 • SQLite\nMaintained by RK RAJA')

@router.message(Command('profile'))
async def profile(m: Message):
    u=m.from_user
    await touch_user(u)
    await m.answer(f'👤 {u.full_name}\nID: <code>{u.id}</code>\nUsername: @{u.username}' if u.username else f'👤 {u.full_name}\nID: <code>{u.id}</code>\nUsername: not set', parse_mode='HTML')

@router.message(Command('stats'))
async def stats(m: Message):
    users=(await fetchone('SELECT COUNT(*) FROM users'))[0]
    groups=(await fetchone('SELECT COUNT(*) FROM groups'))[0]
    await m.answer(f'📊 Bot Stats\nUsers: {users}\nGroups: {groups}')

@router.message(Command('ai'))
async def ai_cmd(m: Message):
    prompt=m.text.partition(' ')[2].strip() if m.text else ''
    if not prompt:
        return await m.reply('Use: /ai your question')
    msg=await m.answer('Thinking...')
    answer=await ask_ai(prompt)
    await msg.edit_text(answer[:4000])

@router.message(Command('coin'))
async def coin(m: Message): await m.answer('🪙 '+random.choice(['Heads','Tails']))

@router.message(Command('dice'))
async def dice(m: Message): await m.answer_dice('🎲')

@router.message(Command('roll'))
async def roll(m: Message):
    try:
        n=int(m.text.split(maxsplit=1)[1]); assert 2 <= n <= 1000000
        await m.answer(f'🎲 Result: {random.randint(1,n)}')
    except Exception: await m.reply('Use: /roll 100 (range 2–1000000)')

@router.message(Command('password'))
async def password(m: Message):
    chars=string.ascii_letters+string.digits+'!@#$%&*_-+'
    await m.answer('Generated password: <code>'+''.join(random.SystemRandom().choice(chars) for _ in range(18))+'</code>', parse_mode='HTML')

@router.message(Command('upper','lower','reverse','count'))
async def text_tools(m: Message):
    cmd=m.text.split(maxsplit=1)[0][1:]
    value=m.text.partition(' ')[2]
    if not value: return await m.reply(f'Use: /{cmd} your text')
    out={'upper':value.upper(),'lower':value.lower(),'reverse':value[::-1],'count':f'Characters: {len(value)} | Words: {len(value.split())}'}[cmd]
    await m.answer(out[:4000])

@router.message(Command('broadcast'))
async def broadcast(m: Message):
    if m.from_user.id != OWNER_ID or not OWNER_ID: return await m.answer('Owner only.')
    body=m.text.partition(' ')[2].strip()
    if not body: return await m.reply('Use: /broadcast message')
    rows=await fetchall('SELECT user_id FROM users')
    sent=0
    for (uid,) in rows:
        try: await m.bot.send_message(uid, body); sent+=1
        except Exception: pass
    await m.answer(f'Broadcast complete: {sent}/{len(rows)} users')
