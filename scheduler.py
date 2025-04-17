from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from datetime import datetime
import pytz

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

async def send_reminder(bot: Bot):
    await bot.send_message(
        chat_id=ADMIN_ID,
        text="🔔 Через 10 минут придёт новая загадка!"
    )

async def setup_scheduler(bot: Bot):
    scheduler.add_job(
        send_reminder,
        "cron",
        hour=8,
        minute=50,
        args=[bot]
    )
    scheduler.start()
