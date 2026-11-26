
import aiohttp

from bot.config import AI_API_KEY, AI_BASE_URL, AI_MODEL


SYSTEM_PROMPT = (
    "You are RK RAJA ULTIMATE XWD's friendly Telegram AI assistant. "
    "Reply naturally in Hindi, Hinglish or English based on the user's language. "
    "Keep replies helpful, clear and concise. Never claim to perform actions "
    "that you have not actually performed."
)


async def ask_ai(prompt: str) -> str:
    if not AI_API_KEY:
        return "AI configure nahi hai. Hosting mein AI_API_KEY set karo."

    url = f"{AI_BASE_URL.rstrip('/')}/chat/completions"

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
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
                url, json=payload, headers=headers
            ) as response:

                data = await response.json(content_type=None)

                if response.status >= 400:
                    return (
                        f"AI provider error ({response.status}). "
                        "API key, model aur quota check karo."
                    )

                choices = data.get("choices", [])
                if not choices:
                    return "AI se reply nahi mila. Dobara try karo."

                content = choices[0].get("message", {}).get("content", "")

                if isinstance(content, str) and content.strip():
                    return content.strip()

                return "AI se empty reply mila."

    except aiohttp.ClientError:
        return "AI server se connection nahi ho paya."
    except TimeoutError:
        return "AI response mein timeout ho gaya."
    except Exception:
        return "AI mein unexpected error aaya."
