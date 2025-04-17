from aiogram.fsm.state import StatesGroup, State

class PuzzleForm(StatesGroup):
    waiting_for_date = State()
    waiting_for_question = State()
    waiting_for_answer = State()
    waiting_for_hint = State()
