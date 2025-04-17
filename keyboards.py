from aiogram.utils.keyboard import ReplyKeyboardBuilder
from emoji import EMOJI_MENU

def main_menu():
    builder = ReplyKeyboardBuilder()
    for button in [
        EMOJI_MENU["rating"],
        EMOJI_MENU["coins"],
        EMOJI_MENU["hint"],
        EMOJI_MENU["friday"]
    ]:
        builder.button(text=button)
    return builder.as_markup(resize_keyboard=True)
