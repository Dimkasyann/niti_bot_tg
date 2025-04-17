import os
import sys
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

# Критически важные строки для Render
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from config import TOKEN
    from handlers import router
except ImportError as e:
    logging.error(f"Import error: {e}")
    # Альтернативный вариант импорта
    from .config import TOKEN
    from .handlers import router

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
