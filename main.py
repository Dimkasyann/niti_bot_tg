# ✅ src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ✅ src/middlewares.py

def setup_middlewares(dp):
    pass  # Пока пусто, добавим позже по мере необходимости

# ✅ src/keyboard.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.config import ADMIN_ID

def main_menu_keyboard(user_id):
    buttons = [
        [InlineKeyboardButton(text="🧠 Рейтинг", callback_data="rating")],
        [InlineKeyboardButton(text="💰 Мои НИТИкоины", callback_data="coins")],
        [InlineKeyboardButton(text="🧩 Подсказка", callback_data="hint")],
        [InlineKeyboardButton(text="🍑 Пошлая пятница", callback_data="friday")],
    ]
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton(text="⚙️ Команды", callback_data="admin_commands")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ✅ src/state.py

from aiogram.fsm.state import State, StatesGroup

class AddPuzzle(StatesGroup):
    waiting_for_date = State()
    waiting_for_question = State()
    waiting_for_answer = State()
    waiting_for_hint = State()

# ✅ src/utils.py

import json
from datetime import datetime, timedelta
from aiogram import Bot
from aiogram.types import Message

from src.keyboard import main_menu_keyboard
from src.config import ADMIN_ID

PUZZLE_FILE = "puzzles.json"

async def send_daily_puzzle(bot: Bot, reminder=False):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(PUZZLE_FILE, "r", encoding="utf-8") as f:
        puzzles = json.load(f)

    for p in puzzles:
        if p["date"] == today:
            question = p["question"]
            hint = p.get("hint", "Подумай хорошенько!")
            break
    else:
        return

    users_file = "users.json"
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []

    for uid in users:
        try:
            if reminder:
                await bot.send_message(uid, "⏰ Через 10 минут прилетит новая загадка! Подготовь мозги 🧠")
            else:
                await bot.send_message(uid, f"🧩 Загадка дня!\n\n<b>{question}</b>", reply_markup=main_menu_keyboard(uid))
        except:
            continue

async def clean_text(text):
    return ''.join(e for e in text.lower().strip() if e.isalnum())

async def get_puzzle_for_today():
    today = datetime.now().strftime("%Y-%m-%d")
    with open(PUZZLE_FILE, "r", encoding="utf-8") as f:
        puzzles = json.load(f)
    for p in puzzles:
        if p["date"] == today:
            return p
    return None

# ✅ src/handlers.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from datetime import datetime, timedelta
import json
import asyncio

from src.keyboard import main_menu_keyboard
from src.utils import clean_text, get_puzzle_for_today
from src.config import ADMIN_ID

router = Router()

user_data = {}
user_coins = {}
hints_shown = {}
answered_users = set()

USERS_FILE = "users.json"

def setup_handlers(dp, bot):
    dp.include_router(router)

@router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.full_name

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f)

    await message.answer(
        f"Привет, друг! 👋\n\nМы — Молодёжный совет НИТИ и рады видеть тебя!\nКаждый день в 09:00 тебя ждёт свежая загадка. Загадай как можно больше — заработай НИТИкоинов 💰 и попади в ТОП!",
        reply_markup=main_menu_keyboard(user_id)
    )

    # Отправим загадку сразу при старте
    puzzle = await get_puzzle_for_today()
    if puzzle:
        await message.answer(f"🧩 Загадка дня!\n\n<b>{puzzle['question']}</b>")
    else:
        await message.answer("🫤 Сегодня загадки нет. Но ты не унывай — приходи завтра!")

@router.callback_query(F.data == "coins")
async def show_coins(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    coins = user_coins.get(user_id, 0)
    await callback.message.edit_text(f"💰 У тебя {coins} НИТИкоинов!")

@router.callback_query(F.data == "hint")
async def show_hint(callback: CallbackQuery):
    user_id = callback.from_user.id
    now = datetime.now()
    if user_id not in hints_shown:
        hints_shown[user_id] = now
        await callback.message.answer("🕒 Подсказка будет доступна через 30 минут! Подожди и подумай ещё!")
    elif now - hints_shown[user_id] >= timedelta(minutes=30):
        puzzle = await get_puzzle_for_today()
        await callback.message.answer(f"🔍 Подсказка: {puzzle['hint']}")
    else:
        remaining = 30 - int((now - hints_shown[user_id]).seconds / 60)
        await callback.message.answer(f"⏳ Подсказка будет доступна через {remaining} мин. Потерпи!")

@router.message()
async def handle_answer(message: Message):
    user_id = str(message.from_user.id)
    if user_id in answered_users:
        await message.answer("📭 Ты уже отгадал сегодняшнюю загадку! Жди следующую 🕘")
        return

    puzzle = await get_puzzle_for_today()
    if not puzzle:
        await message.answer("Сегодня загадки нет. Возвращайся завтра!")
        return

    answer = await clean_text(message.text)
    correct = await clean_text(puzzle["answer"])

    if answer == correct:
        # Подсчёт НИТИкоинов
        position = len(answered_users)
        points = max(1, 10 - position)
        user_coins[user_id] = user_coins.get(user_id, 0) + points
        answered_users.add(user_id)

        now = datetime.now()
        next_riddle_time = datetime.combine(now.date() + timedelta(days=1), datetime.strptime("09:00", "%H:%M").time())
        remaining = next_riddle_time - now
        hours, minutes = divmod(remaining.seconds // 60, 60)

        await message.answer(
            f"🎉 Молодец, ты угадал! Ты получил {points} НИТИкоинов.\nСледующая загадка будет через {hours}ч {minutes}мин. 🧠")
    else:
        await message.answer("❌ Нет, но ты на верном пути! Пробуй ещё раз!")

@router.callback_query(F.data == "rating")
async def show_rating(callback: CallbackQuery):
    top = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)[:10]
    rating = "🏆 Топ-10 мозгов НИТИ:\n\n"
    for i, (uid, coins) in enumerate(top, 1):
        rating += f"{i}. <code>{uid}</code> — {coins} НИТИкоинов\n"
    await callback.message.edit_text(rating)

@router.callback_query(F.data == "admin_commands")
async def show_admin_commands(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.message.answer("⛔ Только администратор может видеть этот список.")
        return

    await callback.message.edit_text(
        "⚙️ Команды администратора:\n\n"
        "/addpuzzle — Добавить новую загадку\n"
        "/restart — Перезапустить бота\n"
        "/stats — Расширенная статистика"
    )
