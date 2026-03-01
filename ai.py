import aiohttp
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


async def generate_ai_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000,
        },
        "messages": [
            {"role": "system", "text": "Ты профессиональный SMM-эксперт."},
            {"role": "user", "text": prompt},
        ],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_URL, json=payload, headers=headers) as resp:
                data = await resp.json()

                if resp.status != 200:
                    return "⚠️ Ошибка AI-сервиса. Попробуйте позже."

                return (
                    data.get("result", {})
                        .get("alternatives", [{}])[0]
                        .get("message", {})
                        .get("text", "⚠️ AI не смог сгенерировать ответ.")
                )

    except Exception:
        return "⚠️ Ошибка соединения с AI-сервисом. Попробуйте позже."