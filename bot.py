import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_LOG_CHANNEL_ID
from db import init_db, async_session, User
from subscription import (
    check_subscription_status,
    decrement_request,
)
from keyboards import subscribe_kb
from ai import generate_ai_response
from datetime import datetime

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id)
            session.add(user)
            await session.commit()

    await message.answer(
        "🚀 Добро пожаловать в AI-SMM ассистента!\n\n"
        "🎁 Вам доступно 5 бесплатных AI-запросов.\n\n"
        "После окончания бесплатных запросов потребуется подписка.\n\n"
        "💎 Доступные тарифы:\n"
        "• Стандарт — 690₽ / 1 месяц\n"
        "• Оптимальный — 3600₽ / 6 месяцев\n"
        "• Премиум — 6600₽ / 12 месяцев"
    )


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    user_text = message.text

    # Проверка подписки
    status, until_date = await check_subscription_status(user_id)

    async with async_session() as session:
        user = await session.get(User, user_id)

    # 🔴 Нет подписки или истекла
    if status in ["no_subscription", "expired"]:
        if user and user.free_requests > 0:
            pass
        else:
            await message.answer(
                "❌ Бесплатные запросы закончились или подписка истекла.\n\n"
                "Выберите тариф для продолжения:",
                reply_markup=subscribe_kb(user_id)
            )
            return

    # 🟡 Подписка скоро заканчивается
    if status == "expiring_soon":
        await message.answer(
            f"⚠️ Ваша подписка заканчивается "
            f"{until_date.strftime('%d.%m.%Y')}.\n\n"
            "Рекомендуем продлить заранее 👇",
            reply_markup=subscribe_kb(user_id)
        )

    # Проверка лимита запросов
    can_proceed = await decrement_request(user_id)

    if not can_proceed:
        await message.answer(
            "❌ Лимит запросов по тарифу исчерпан.\n\n"
            "Выберите тариф для продления:",
            reply_markup=subscribe_kb(user_id)
        )
        return

    # Генерация AI-ответа
    ai_response = await generate_ai_response(user_text)

    # Ответ пользователю
    await message.answer(ai_response)

    # Логирование
    log_text = (
        f"👤 Пользователь: @{username}\n"
        f"🆔 user_id: {user_id}\n"
        f"📅 Дата: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}\n"
        f"💬 Сообщение: {user_text}\n"
        f"🤖 Ответ AI: {ai_response}"
    )

    await bot.send_message(ADMIN_LOG_CHANNEL_ID, log_text)