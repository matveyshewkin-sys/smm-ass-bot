from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import PAY_URL


def subscribe_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Стандарт — 690₽ / 1 месяц",
                    url=f"{PAY_URL}?user_id={user_id}&tariff=standard",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚀 Оптимальный — 3600₽ / 6 месяцев",
                    url=f"{PAY_URL}?user_id={user_id}&tariff=optimal",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Премиум — 6600₽ / 12 месяцев",
                    url=f"{PAY_URL}?user_id={user_id}&tariff=premium",
                )
            ],
        ]
    )