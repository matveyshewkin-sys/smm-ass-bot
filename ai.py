import aiohttp
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

YANDEX_URL = "https://llm.api.cloud.yandex.net/v1/chat/completions"

async def generate_ai_response(prompt: str) -> str:
    if not YANDEX_API_KEY:
        return "❌ Ошибка: API ключ Яндекса не установлен."

    if not YANDEX_FOLDER_ID:
        return "❌ Ошибка: YANDEX_FOLDER_ID не указан."

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "folderId": YANDEX_FOLDER_ID,
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
                if resp.status != 200:
                    data = await resp.json()
                    error_msg = data.get("error", {}).get("message") or str(data)
                    return f"❌ Ошибка AI: {error_msg}"

                data = await resp.json()
                choices = data.get("choices")
                if not choices or "message" not in choices[0]:
                    return f"❌ Ошибка AI: неверный формат ответа {data}"

                return choices[0]["message"]["content"]

    except Exception as e:
        return f"❌ Ошибка соединения с AI: {str(e)}"