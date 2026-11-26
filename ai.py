import aiohttp
from bot.config import AI_API_KEY, AI_BASE_URL, AI_MODEL

async def ask_ai(prompt: str) -> str:
    if not AI_API_KEY:
        return 'AI abhi configure nahi hai. Hosting ke environment variables mein AI_API_KEY set karo.'
    url = f'{AI_BASE_URL}/chat/completions'
    payload = {'model': AI_MODEL, 'messages': [{'role':'system','content':'You are a helpful, friendly Telegram assistant. Keep replies concise and safe.'},{'role':'user','content':prompt}], 'temperature':0.7}
    headers = {'Authorization': f'Bearer {AI_API_KEY}', 'Content-Type':'application/json'}
    timeout = aiohttp.ClientTimeout(total=45)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json(content_type=None)
            if response.status >= 400:
                return f'AI provider error ({response.status}). API key, model aur quota check karo.'
            return data.get('choices',[{}])[0].get('message',{}).get('content','AI se reply nahi mila.')
