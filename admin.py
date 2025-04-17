# admin.py
async def show_commands(message):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer("Доступные команды:\n/start\n/rating\n/commands\n/hint")
