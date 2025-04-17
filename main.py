import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
from config import TOKEN, WEBHOOK_URL, PORT
from handlers import router
from scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)

async def on_startup(bot: Bot):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    await setup_scheduler(bot)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    app = web.Application()
    app.on_startup.append(lambda _: on_startup(bot))
    setup_application(app, dp, bot=bot)
    
    await web._run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
