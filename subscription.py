from datetime import datetime, timedelta
from db import async_session, User

# 🔹 Тарифы
TARIFFS = {
    "standard": {
        "name": "Стандарт",
        "days": 30,
        "price": 690,
        "requests": 10000,
    },
    "optimal": {
        "name": "Оптимальный",
        "days": 180,  # 6 месяцев
        "price": 3600,
        "requests": 60000,
    },
    "premium": {
        "name": "Премиум",
        "days": 365,  # 12 месяцев
        "price": 6600,
        "requests": 130000,
    },
}


async def activate_subscription(user_id: int, tariff_key: str):
    if tariff_key not in TARIFFS:
        return False

    tariff = TARIFFS[tariff_key]

    async with async_session() as session:
        user = await session.get(User, user_id)

        if not user:
            user = User(id=user_id)
            session.add(user)

        now = datetime.utcnow()

        # если подписка активна — продлеваем
        if user.subscription_until and user.subscription_until > now:
            user.subscription_until += timedelta(days=tariff["days"])
        else:
            user.subscription_until = now + timedelta(days=tariff["days"])

        user.paid_requests_left += tariff["requests"]
        user.expiry_notified = False

        await session.commit()

    return True


# 🔹 Проверка статуса подписки
async def check_subscription_status(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)

        if not user or not user.subscription_until:
            return "no_subscription", None

        now = datetime.utcnow()

        if user.subscription_until < now:
            return "expired", user.subscription_until

        # если осталось меньше 3 дней
        if user.subscription_until - now <= timedelta(days=3):
            return "expiring_soon", user.subscription_until

        return "active", user.subscription_until


# 🔹 Уменьшение доступных запросов
async def decrement_request(user_id: int):
    async with async_session() as session:
        user = await session.get(User, user_id)

        if not user:
            return False

        # Если есть оплаченные запросы
        if user.paid_requests_left > 0:
            user.paid_requests_left -= 1
            await session.commit()
            return True

        # Если есть бесплатные запросы
        if user.free_requests > 0:
            user.free_requests -= 1
            await session.commit()
            return True

        return False