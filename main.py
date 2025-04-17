# main.py
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
import asyncio, logging, os
from src.config import TOKEN, WEBHOOK_URL, PORT
from src.handlers import register_all_handlers
from src.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    register_all_handlers(dp)
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
    ])
    
    asyncio.create_task(start_scheduler(bot))

    from aiogram.webhook.aiohttp_server import setup_application
    from aiohttp import web

    app = web.Application()
    dp.startup.register(lambda _: logging.info("Бот запущен."))
    dp.shutdown.register(lambda _: logging.info("Бот остановлен."))

    setup_application(app, dp, bot=bot)
    app.on_shutdown.append(lambda _: bot.session.close())

    web.run_app(app, host="0.0.0.0", port=int(PORT))

if __name__ == '__main__':
    asyncio.run(main())

# src/config.py
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = os.getenv("PORT", 10000)

# src/messages.py
WELCOME = "<b>Привет, друг!</b> 👋\n\nМы — Молодёжный совет НИТИ 👨‍🔬\nКаждое утро в 09:00 мы будем отправлять тебе крутую загадку 🧠\n\nБудь первым, кто её отгадает, и забирай 10 НИТИкоинов! 🪙\n\nТы готов? Жми /start или кнопки ниже ⬇️"
MOTIVATION = [
    "Ты можешь больше, чем думаешь! 💪",
    "Каждая загадка — шаг к успеху 🚀",
    "МС НИТИ — самые смекалистые! 🧠"
]

# src/utils.py
import string

def clean_text(text):
    return ''.join(c.lower() for c in text.strip() if c not in string.punctuation and c != ' ')

def answers_match(user_answer, correct_answer):
    return clean_text(user_answer) == clean_text(correct_answer)

# src/database.py
import json, os
PUZZLES_FILE = "puzzles.json"
SCORES_FILE = "user_scores.json"

def load_puzzles():
    if not os.path.exists(PUZZLES_FILE): return {}
    with open(PUZZLES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_puzzles(data):
    with open(PUZZLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_scores():
    if not os.path.exists(SCORES_FILE): return {}
    with open(SCORES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_scores(data):
    with open(SCORES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# src/scheduler.py
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from src.database import load_puzzles
from src.handlers.menu import send_daily_puzzle, notify_puzzle_coming

async def start_scheduler(bot: Bot):
    while True:
        now = datetime.now()
        next_8_50 = now.replace(hour=8, minute=50, second=0, microsecond=0)
        next_9_00 = now.replace(hour=9, minute=0, second=0, microsecond=0)

        if now >= next_9_00:
            next_9_00 += timedelta(days=1)
        if now >= next_8_50:
            next_8_50 += timedelta(days=1)

        await asyncio.sleep((next_8_50 - now).total_seconds())
        await notify_puzzle_coming(bot)
        await asyncio.sleep(600)  # 10 мин
        await send_daily_puzzle(bot)

# src/handlers/__init__.py
from aiogram import Dispatcher
from .start import start_router
from .menu import menu_router
from .hint import hint_router
from .rating import rating_router
from .admin import admin_router

def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(hint_router)
    dp.include_router(rating_router)
    dp.include_router(admin_router)
