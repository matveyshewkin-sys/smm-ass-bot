import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from config import BOT_TOKEN, ADMIN_LOG_CHANNEL_ID
from db import async_session, User
from subscription import check_subscription_status, decrement_request
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
            user = User(
                id=user_id,
                free_requests=5,
                paid_requests_left=0
            )
            session.add(user)
            await session.commit()

    await message.answer("Скорее задавайте свой вопрос ⬇️")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    user_text = message.text

    async with async_session() as session:
        user = await session.get(User, user_id)

        if not user:
            user = User(
                id=user_id,
                free_requests=5,
                paid_requests_left=0
            )
            session.add(user)
            await session.commit()

    status, until_date = await check_subscription_status(user_id)

    if user.free_requests <= 0 and status in ["no_subscription", "expired"]:
        await message.answer(
            "❌ Бесплатные запросы закончились или подписка истекла.\n\n"
            "Выберите тариф для продолжения:",
            reply_markup=subscribe_kb(user_id)
        )
        return

    if status == "expiring_soon":
        await message.answer(
            f"⚠️ Ваша подписка заканчивается "
            f"{until_date.strftime('%d.%m.%Y')}.\n\n"
            "Рекомендуем продлить заранее 👇",
            reply_markup=subscribe_kb(user_id)
        )

    can_proceed = await decrement_request(user_id)

    if not can_proceed:
        await message.answer(
            "❌ Лимит запросов по тарифу исчерпан.\n\n"
            "Выберите тариф для продления:",
            reply_markup=subscribe_kb(user_id)
        )
        return

    processing_msg = await message.answer("⏳ Генерирую ответ...")

    ai_response = await generate_ai_response(user_text)

    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=processing_msg.message_id,
        text=ai_response
    )

    log_text = (
        f"👤 Пользователь: @{username}\n"
        f"🆔 user_id: {user_id}\n"
        f"📅 Дата: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}\n"
        f"💬 Сообщение: {user_text}\n"
        f"🤖 Ответ AI: {ai_response}"
    )

    if ADMIN_LOG_CHANNEL_ID:
        await bot.send_message(ADMIN_LOG_CHANNEL_ID, log_text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())