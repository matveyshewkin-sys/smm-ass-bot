from fastapi import APIRouter, Request
from yookassa import Configuration, Payment
from yookassa.webhook_notification.webhook_notification import WebhookNotification  # <- исправлено
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, PAY_URL
from subscription import activate_subscription, TARIFFS

router = APIRouter()

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


@router.post("/create-payment")
async def create_payment(data: dict):
    user_id = data.get("user_id")
    tariff_key = data.get("tariff")

    if tariff_key not in TARIFFS:
        return {"error": "invalid tariff"}

    tariff = TARIFFS[tariff_key]

    payment = Payment.create({
        "amount": {
            "value": str(tariff["price"]),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": PAY_URL
        },
        "capture": True,
        "description": f"Подписка {tariff['name']}",
        "metadata": {
            "user_id": str(user_id),
            "tariff": tariff_key
        }
    })

    return {"confirmation_url": payment.confirmation.confirmation_url}


@router.post("/yookassa")
async def yookassa_webhook(request: Request):
    body = await request.body()
    notification = WebhookNotification.factory(body)

    if notification.event == "payment.succeeded":
        payment = notification.object
        user_id = int(payment.metadata.get("user_id"))
        tariff_key = payment.metadata.get("tariff")

        await activate_subscription(user_id, tariff_key)

        tariff = TARIFFS[tariff_key]

        from bot import bot  # избегаем циклические импорты
        await bot.send_message(user_id, "✅ Оплата прошла успешно")
        await bot.send_message(
            user_id,
            f"🎉 Тариф «{tariff['name']}» активирован!\n\n"
            f"📅 Действует {tariff['days']} дней\n"
            f"📊 Доступно {tariff['requests']} запросов"
        )

    return {"status": "ok"}