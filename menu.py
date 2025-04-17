# menu.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Рейтинг"))
main_menu.add(KeyboardButton("Мои НИТИкоины"))
main_menu.add(KeyboardButton("Подсказка"))
main_menu.add(KeyboardButton("Пошлая пятница"))
