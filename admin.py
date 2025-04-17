from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import PuzzleForm
from database import save_puzzle
from config import ADMIN_ID
from keyboards import admin_kb

router = Router()

@router.message(F.text == "🛠️ Команды", F.from_user.id == ADMIN_ID)
async def show_commands(message: Message):
    cmds = [
        "🔧 <b>Админ-команды:</b>",
        "/add_puzzle - Добавить загадку",
        "/stats - Статистика",
        "/broadcast - Рассылка",
        "/restart - Перезапуск бота"
    ]
    await message.answer("\n".join(cmds), reply_markup=admin_kb())

@router.message(F.text == "➕ Добавить загадку", F.from_user.id == ADMIN_ID)
async def add_puzzle_start(message: Message, state: FSMContext):
    await message.answer("Введите дату загадки (ГГГГ-ММ-ДД):")
    await state.set_state(PuzzleForm.waiting_for_date)
