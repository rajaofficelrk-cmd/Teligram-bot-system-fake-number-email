
import aiohttp

from bot.config import AI_API_KEY, AI_BASE_URL, AI_MODEL

SYSTEM_PROMPT = """
You are RK RAJA ULTIMATE XWD AI assistant.
Talk naturally like a friendly human.
Understand Hindi, Hinglish and English.
Reply in the same language as the user.
Remember the conversation context provided to you.
Be helpful, friendly and concise.
Never pretend to perform actions you cannot perform.
"""

async def ask_ai(prompt: str, history=None) -> str:
    if not AI_API_KEY:
        return "AI configure nahi hai. Hosting mein AI_API_KEY set karo."

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history[-10:])

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }

    timeout = aiohttp.ClientTimeout(total=45)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{AI_BASE_URL.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers
            ) as response:

                data = await response.json(content_type=None)

                if response.status >= 400:
                    return f"AI provider error: {response.status}"

                choices = data.get("choices", [])
                if not choices:
                    return "AI se reply nahi mila."

                answer = choices[0].get("message", {}).get("content", "")
                return answer.strip() if isinstance(answer, str) and answer.strip() else "AI reply empty hai."

    except (aiohttp.ClientError, TimeoutError):
        return "AI server se connection nahi ho paya."
    except Exception:
        return "AI mein unexpected error aaya."
