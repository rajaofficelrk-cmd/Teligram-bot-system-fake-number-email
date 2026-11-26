import re, time
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated
from aiogram.exceptions import TelegramBadRequest
from bot.database.db import ensure_group, group, set_group_field, set_setting, get_setting, execute, fetchone, fetchall

router=Router()

def is_group(m): return m.chat.type in ('group','supergroup')
async def admin_ok(m):
    if not is_group(m): return False
    member=await m.bot.get_chat_member(m.chat.id,m.from_user.id)
    return member.status in ('administrator','creator')
async def require_admin(m):
    if not is_group(m): await m.answer('Ye command group mein use karo.'); return False
    if not await admin_ok(m): await m.answer('Sirf group admins use kar sakte hain.'); return False
    await ensure_group(m.chat); return True

@router.message(Command('gclock'))
async def lock_title(m:Message):
    if not await require_admin(m): return
    await set_group_field(m.chat.id,'saved_title',m.chat.title or '')
    await set_group_field(m.chat.id,'title_lock',1)
    await m.answer('🔒 Group title lock ON. Bot ko Manage Chat Info permission do.')

@router.message(Command('gcunlock'))
async def unlock_title(m:Message):
    if not await require_admin(m): return
    await set_group_field(m.chat.id,'title_lock',0); await m.answer('🔓 Group title lock OFF.')

@router.message(Command('setgclock'))
async def set_locked_title(m:Message):
    if not await require_admin(m): return
    title=m.text.partition(' ')[2].strip()
    if not title: return await m.reply('Use: /setgclock New Group Name')
    if len(title)>128: return await m.reply('Title max 128 characters.')
    await set_group_field(m.chat.id,'saved_title',title)
    try:
        await m.bot.set_chat_title(m.chat.id,title)
        await set_group_field(m.chat.id,'title_lock',1)
        await m.answer('✅ Locked title saved and applied.')
    except TelegramBadRequest as e: await m.answer(f'Title change failed. Check bot admin permission. ({e.message})')

@router.message(Command('lockstatus'))
async def lock_status(m:Message):
    if not is_group(m): return await m.answer('Group only.')
    await ensure_group(m.chat); row=await group(m.chat.id)
    await m.answer(f"Title lock: {'ON' if row[3] else 'OFF'}\nSaved title: {row[2] or '-'}")

async def toggle(m, field, label):
    if not await require_admin(m): return
    arg=m.text.split(maxsplit=1)[1].lower() if len(m.text.split())>1 else ''
    if arg not in ('on','off'): return await m.reply(f'Use: /{label.lower().replace(" ","")} on|off')
    await set_group_field(m.chat.id,field,1 if arg=='on' else 0)
    await m.answer(f'{label}: {arg.upper()}')

@router.message(Command('antilink'))
async def antilink(m): await toggle(m,'antilink','Anti-link')
@router.message(Command('antiflood'))
async def antiflood(m): await toggle(m,'antiflood','Anti-flood')
@router.message(Command('welcome'))
async def welcome_toggle(m): await toggle(m,'welcome','Welcome')

@router.message(Command('setwelcome'))
async def set_welcome(m):
    if not await require_admin(m): return
    val=m.text.partition(' ')[2].strip()
    if not val: return await m.reply('Use {name} for member name. Example: /setwelcome Welcome {name}!')
    await set_group_field(m.chat.id,'welcome_text',val[:1000]); await m.answer('Welcome message updated.')

@router.message(Command('rules'))
async def rules(m):
    if not is_group(m): return await m.answer('Group only.')
    val=await get_setting(m.chat.id,'rules','Rules abhi set nahi hain.')
    await m.answer(val)

@router.message(Command('setrules'))
async def set_rules(m):
    if not await require_admin(m): return
    val=m.text.partition(' ')[2].strip()
    if not val: return await m.reply('Use: /setrules Your group rules')
    await set_setting(m.chat.id,'rules',val[:4000]); await m.answer('Group rules saved.')

@router.message(Command('note'))
async def note(m):
    if not await require_admin(m): return
    parts=m.text.split(maxsplit=2)
    if len(parts)<3: return await m.reply('Use: /note name note text')
    await execute('INSERT INTO notes(chat_id,name,value) VALUES(?,?,?) ON CONFLICT(chat_id,name) DO UPDATE SET value=excluded.value',(m.chat.id,parts[1].lower(),parts[2][:3000]))
    await m.answer(f'Note {parts[1]} saved.')

@router.message(Command('get'))
async def get_note(m):
    if not is_group(m): return
    name=m.text.partition(' ')[2].strip().lower()
    row=await fetchone('SELECT value FROM notes WHERE chat_id=? AND name=?',(m.chat.id,name))
    await m.answer(row[0] if row else 'Note nahi mila.')

@router.message(Command('notes'))
async def notes(m):
    if not is_group(m): return
    rows=await fetchall('SELECT name FROM notes WHERE chat_id=? ORDER BY name',(m.chat.id,))
    await m.answer('Saved notes: '+(', '.join(r[0] for r in rows) if rows else 'none'))

@router.message(Command('warn','warnings','clearwarns','kick','ban','unban','mute','unmute','del','pin','unpin'))
async def moderation(m:Message):
    if not await require_admin(m): return
    cmd=m.text.split()[0][1:]
    target=m.reply_to_message.from_user if m.reply_to_message else None
    if cmd in ('del','pin','unpin'):
        try:
            if cmd=='del':
                if not m.reply_to_message: return await m.reply('Kisi message par reply karke /del likho.')
                await m.bot.delete_message(m.chat.id,m.reply_to_message.message_id)
            elif cmd=='pin':
                if not m.reply_to_message: return await m.reply('Reply karke /pin likho.')
                await m.bot.pin_chat_message(m.chat.id,m.reply_to_message.message_id)
            else: await m.bot.unpin_chat_message(m.chat.id)
            return
        except TelegramBadRequest as e: return await m.answer(f'Action failed: {e.message}')
    if cmd=='unban':
        try:
            uid=int(m.text.split(maxsplit=1)[1]); await m.bot.unban_chat_member(m.chat.id,uid); return await m.answer('User unbanned.')
        except Exception: return await m.reply('Use: /unban USER_ID')
    if not target: return await m.reply('Target member ke message par reply karo.')
    if target.id==m.from_user.id: return await m.reply('Khud par ye action nahi kar sakte.')
    if cmd=='warnings':
        row=await fetchone('SELECT count FROM warnings WHERE chat_id=? AND user_id=?',(m.chat.id,target.id)); return await m.answer(f'Warnings: {row[0] if row else 0}')
    if cmd=='clearwarns':
        await execute('DELETE FROM warnings WHERE chat_id=? AND user_id=?',(m.chat.id,target.id)); return await m.answer('Warnings cleared.')
    try:
        if cmd=='warn':
            await execute('INSERT INTO warnings(chat_id,user_id,count) VALUES(?,?,1) ON CONFLICT(chat_id,user_id) DO UPDATE SET count=count+1',(m.chat.id,target.id))
            row=await fetchone('SELECT count FROM warnings WHERE chat_id=? AND user_id=?',(m.chat.id,target.id)); return await m.answer(f'⚠️ {target.full_name}: warning {row[0]}/3')
        if cmd=='kick': await m.bot.ban_chat_member(m.chat.id,target.id); await m.bot.unban_chat_member(m.chat.id,target.id); return await m.answer('Member removed.')
        if cmd=='ban': await m.bot.ban_chat_member(m.chat.id,target.id); return await m.answer('Member banned.')
        if cmd=='mute':
            minutes=int(m.text.split(maxsplit=1)[1]); minutes=max(1,min(minutes,10080))
            from datetime import datetime, timedelta, timezone
            await m.bot.restrict_chat_member(m.chat.id,target.id, permissions=__import__('aiogram').types.ChatPermissions(can_send_messages=False), until_date=datetime.now(timezone.utc)+timedelta(minutes=minutes))
            return await m.answer(f'Member muted for {minutes} minutes.')
        if cmd=='unmute':
            from aiogram.types import ChatPermissions
            await m.bot.restrict_chat_member(m.chat.id,target.id,permissions=ChatPermissions(can_send_messages=True,can_send_audios=True,can_send_documents=True,can_send_photos=True,can_send_videos=True,can_send_video_notes=True,can_send_voice_notes=True,can_send_polls=True,can_send_other_messages=True,can_add_web_page_previews=True)); return await m.answer('Member unmuted.')
    except (ValueError,TelegramBadRequest) as e: await m.answer(f'Action failed: {e}')

@router.message(F.new_chat_members)
async def greet(m:Message):
    await ensure_group(m.chat); row=await group(m.chat.id)
    if row and row[6]:
        for u in m.new_chat_members:
            try: await m.answer(row[7].replace('{name}',u.full_name))
            except Exception: pass

@router.message(F.left_chat_member)
async def goodbye(m:Message):
    await m.answer(f'Goodbye {m.left_chat_member.full_name}!')

@router.message(F.chat.type.in_({'group','supergroup'}))
async def group_guard(m:Message):
    if not m.from_user or m.from_user.is_bot: return
    await ensure_group(m.chat); row=await group(m.chat.id)
    if not row: return
    # Never moderate administrators or the group creator.
    try:
        member=await m.bot.get_chat_member(m.chat.id,m.from_user.id)
        if member.status in ('administrator','creator'): return
    except Exception: pass
    if row[3] and m.chat.title != row[2]:
        try: await m.bot.set_chat_title(m.chat.id,row[2])
        except Exception: pass
    if row[4] and m.text and re.search(r'(https?://|www\.|t\.me/)',m.text,re.I):
        try: await m.delete()
        except Exception: pass
        return
    if row[5]:
        now=time.time(); key=f'flood:{m.chat.id}:{m.from_user.id}'
        last=float(await get_setting(m.chat.id,key,'0'))
        await set_setting(m.chat.id,key,str(now))
        if now-last < 1.2:
            try: await m.delete()
            except Exception: pass

@router.chat_member()
async def title_watch(event:ChatMemberUpdated):
    # Telegram does not expose every title change as a chat_member update; guard also checks incoming messages.
    await ensure_group(event.chat)
