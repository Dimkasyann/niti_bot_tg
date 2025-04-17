from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from datetime import datetime, timedelta
import json, asyncio
import os

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

async def send_reminder(bot: Bot, chat_ids: list):
    for chat_id in chat_ids:
        await bot.send_message(chat_id, "🔔 В 09:00 придёт свеженькая загадка!")

async def send_puzzle(bot: Bot, chat_ids: list):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open("puzzles.json", encoding="utf-8") as f:
            puzzles = json.load(f)
        puzzle = puzzles[today]
        for chat_id in chat_ids:
            await bot.send_message(chat_id, f"🧠 *Загадка дня!*\n\n{puzzle['question']}", parse_mode="Markdown")
    except:
        for chat_id in chat_ids:
            await bot.send_message(chat_id, "❌ Сегодня загадка не найдена. Админ, добавь её!")

def setup_scheduler(bot: Bot, chat_ids: list):
    scheduler.add_job(send_reminder, "cron", hour=8, minute=50, args=[bot, chat_ids])
    scheduler.add_job(send_puzzle, "cron", hour=9, minute=0, args=[bot, chat_ids])
    scheduler.start()
