# main.py
import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TOKEN, WEBHOOK_URL, PORT, ADMIN_ID
from menu import main_menu
from rating import show_rating
from admin import show_commands
from hint import check_hint

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Функция для отправки загадки
async def send_puzzle():
    with open('puzzles.json', 'r') as f:
        puzzles = json.load(f)
    # Пример для первой загадки
    puzzle = puzzles.get("2025-04-17")
    await bot.send_message(chat_id=ADMIN_ID, text=f"Загадка: {puzzle['question']}")

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет, друг! Мы из Молодёжного совета НИТИ. Загадки будут каждый день в 09:00! Жди!\nТвои НИТИкоины: 0", reply_markup=main_menu)

@dp.message_handler(commands=["rating"])
async def rating(message: types.Message):
    await show_rating(message)

@dp.message_handler(commands=["commands"])
async def commands(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        await show_commands(message)

@dp.message_handler(commands=["hint"])
async def hint(message: types.Message):
    await check_hint(message)

if __name__ == '__main__':
    executor.start_polling(dp)
