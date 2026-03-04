import aiohttp
from config import YANDEX_API_KEY

YANDEX_URL = "https://llm.api.cloud.yandex.net/v1/chat/completions"

async def generate_ai_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt://b1g7sbvhcup1f7boq36/yandexgpt/latest",
        "messages": [
            {"role": "system", "content": "Ты профессиональный SMM-эксперт."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.6,
        "max_tokens": 1500,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_URL, json=payload, headers=headers) as resp:
                data = await resp.json()

                if resp.status != 200:
                    return f"Ошибка AI: {data}"

                return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Ошибка соединения: {str(e)}"