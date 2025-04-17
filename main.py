import asyncio
import logging
import json
import string
from datetime import datetime, timedelta
import os
import pytz
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# === Load environment variables === #
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PORT = int(os.getenv("PORT", 3000))
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
BASE_WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# === Init bot and dispatcher === #
session = AiohttpSession()
bot = Bot(token=BOT_TOKEN, session=session, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# === Time zone === #
moscow_tz = pytz.timezone("Europe/Moscow")

# === Puzzle file === #
PUZZLE_FILE = "puzzles.json"

# === State Machine for Adding Puzzle === #
class PuzzleForm(StatesGroup):
    waiting_for_date = State()
    waiting_for_question = State()
    waiting_for_answer = State()
    waiting_for_hint = State()
    waiting_for_friday = State()

# === Utilities === #
def load_puzzles():
    if not os.path.exists(PUZZLE_FILE):
        return []
    with open(PUZZLE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_puzzles(puzzles):
    with open(PUZZLE_FILE, "w", encoding="utf-8") as f:
        json.dump(puzzles, f, ensure_ascii=False, indent=2)

def normalize_answer(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation)).strip()
    return "".join(text.split())

def get_today_puzzle():
    today = datetime.now(moscow_tz).strftime("%Y-%m-%d")
    puzzles = load_puzzles()
    for p in puzzles:
        if p['date'] == today:
            return p
    return None

user_coins = {}
user_answers = {}

# === Keyboards === #
def main_keyboard():
    kb = [[
        InlineKeyboardButton(text="💰 Мои НИТИкоины", callback_data="my_coins"),
        InlineKeyboardButton(text="📊 Рейтинг", callback_data="rating")
    ], [
        InlineKeyboardButton(text="🧠 Подсказка", callback_data="hint"),
        InlineKeyboardButton(text="😏 Пошлая пятница", callback_data="friday")
    ]]
    if ADMIN_ID:
        kb.append([InlineKeyboardButton(text="🎩 Команды", callback_data="admin")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

# === Scheduler Tasks === #
async def send_daily_puzzle():
    puzzle = get_today_puzzle()
    if puzzle:
        text = f"🧩 <b>Загадка дня ({puzzle['date']})</b>\n{puzzle['question']}"
        await bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=main_keyboard())

async def send_reminder():
    await bot.send_message(chat_id=ADMIN_ID, text="⏰ Через 10 минут выйдет новая загадка!")

async def scheduler():
    while True:
        now = datetime.now(moscow_tz)
        if now.strftime("%H:%M") == "08:50":
            await send_reminder()
        elif now.strftime("%H:%M") == "09:00":
            await send_daily_puzzle()
        await asyncio.sleep(60)

# === Command Handlers === #
@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Добро пожаловать в QuizMCBot!", reply_markup=main_keyboard())

@router.callback_query(F.data == "my_coins")
async def show_coins(callback: CallbackQuery):
    coins = user_coins.get(callback.from_user.id, 0)
    await callback.message.answer(f"💰 У тебя {coins} НИТИкоинов!")

@router.callback_query(F.data == "rating")
async def show_rating(callback: CallbackQuery):
    top = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)[:10]
    text = "📊 <b>ТОП-10</b>\n"
    for i, (uid, score) in enumerate(top, 1):
        text += f"{i}. <a href='tg://user?id={uid}'>Пользователь</a> — {score} 🪙\n"
    await callback.message.answer(text)

@router.callback_query(F.data == "hint")
async def show_hint(callback: CallbackQuery):
    puzzle = get_today_puzzle()
    if not puzzle:
        await callback.message.answer("Сегодня загадка ещё не загружена.")
        return
    await callback.message.answer(f"🧠 Подсказка: {puzzle['hints'][0]}")

@router.callback_query(F.data == "friday")
async def show_friday(callback: CallbackQuery):
    puzzle = get_today_puzzle()
    if puzzle and puzzle.get("is_friday"):
        await callback.message.answer("😏 Сегодня Пошлая пятница! Бонус +3 НИТИкоина!")
    else:
        await callback.message.answer("Сегодня обычный день 🙃")

@router.callback_query(F.data == "admin")
async def admin_panel(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    text = "🎩 Команды админа:\n/addpuzzle — добавить загадку\n/restart — перезапуск бота"
    await callback.message.answer(text)

# === Answer Handler === #
@router.message()
async def handle_answer(message: Message):
    puzzle = get_today_puzzle()
    if not puzzle:
        return
    if message.from_user.id in user_answers.get(puzzle['date'], []):
        return await message.answer("⛔ Ты уже отвечал сегодня!")
    if normalize_answer(message.text) == normalize_answer(puzzle['answer']):
        pos = len(user_answers.setdefault(puzzle['date'], [])) + 1
        reward = max(11 - pos, 1) + (3 if puzzle.get("is_friday") else 0)
        user_coins[message.from_user.id] = user_coins.get(message.from_user.id, 0) + reward
        user_answers[puzzle['date']].append(message.from_user.id)
        await message.answer(f"🎉 Правильно! Ты получаешь {reward} НИТИкоинов!")
    else:
        await message.answer("❌ Неправильно, попробуй ещё раз!")

# === Admin: Add Puzzle === #
@router.message(F.text == "/addpuzzle")
async def start_add_puzzle(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🗓 Введи дату загадки в формате ГГГГ-ММ-ДД")
    await state.set_state(PuzzleForm.waiting_for_date)

@router.message(PuzzleForm.waiting_for_date)
async def puzzle_date_entered(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer("🧠 Введи текст загадки")
    await state.set_state(PuzzleForm.waiting_for_question)

@router.message(PuzzleForm.waiting_for_question)
async def puzzle_question_entered(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("✅ Введи правильный ответ")
    await state.set_state(PuzzleForm.waiting_for_answer)

@router.message(PuzzleForm.waiting_for_answer)
async def puzzle_answer_entered(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    await message.answer("💡 Введи подсказку")
    await state.set_state(PuzzleForm.waiting_for_hint)

@router.message(PuzzleForm.waiting_for_hint)
async def puzzle_hint_entered(message: Message, state: FSMContext):
    await state.update_data(hint=message.text)
    await message.answer("Сегодня пятница и загадка пошлая? (да/нет)")
    await state.set_state(PuzzleForm.waiting_for_friday)

@router.message(PuzzleForm.waiting_for_friday)
async def puzzle_friday_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    puzzles = load_puzzles()
    puzzles.append({
        "date": data['date'],
        "question": data['question'],
        "answer": data['answer'],
        "hints": [data['hint']],
        "is_friday": message.text.lower() == "да"
    })
    save_puzzles(puzzles)
    await message.answer("✅ Загадка успешно добавлена!")
    await state.clear()

# === Admin Restart === #
@router.message(F.text == "/restart")
async def restart_bot(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔄 Перезапуск... (условный)")

# === Launch === #
async def on_startup(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="addpuzzle", description="Добавить загадку (только админ)"),
        BotCommand(command="restart", description="Перезапуск бота (только админ)")
    ], scope=BotCommandScopeDefault())

app = web.Application()
app['bot'] = bot
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")
    asyncio.create_task(scheduler())
    return app

if __name__ == '__main__':
    web.run_app(main(), port=PORT)
