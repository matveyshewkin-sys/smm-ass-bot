import asyncio
from fastapi import FastAPI, Request
from aiogram.types import Update
from bot import dp, bot
from payments import router as payments_router
from db import init_db
import os

app = FastAPI()

# подключаем платежи
app.include_router(payments_router)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # будет из Railway

@app.on_event("startup")
async def on_startup():
    await init_db()

    # удаляем старый webhook если был
    await bot.delete_webhook(drop_pending_updates=True)

    # ставим новый webhook
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "running"}