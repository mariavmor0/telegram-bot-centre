import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from telegram import Update
from app.bot import get_application

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

telegram_app = get_application()
app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    if WEBHOOK_URL:
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        await telegram_app.start()
        print(f"Webhook установлен: {WEBHOOK_URL}")
    else:
        print("Запускаем polling")
        await telegram_app.start()
        await telegram_app.run_polling()

@app.on_event("shutdown")
async def on_shutdown():
    await telegram_app.stop()
    print("Бот остановлен")

@app.get("/")
async def root():
    return {"status": "Bot is running"}