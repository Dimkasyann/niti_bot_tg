def get_status(score: int) -> str:
    if score >= 100:
        return "🧠 Гений НИТИ"
    elif score >= 50:
        return "🔥 Мозговой штурмовик"
    elif score >= 20:
        return "💡 Мозг включён"
    elif score >= 1:
        return "👶 Учёный-первоход"
    return "🫥 Без НИТИкоинов"

EMOJI_MENU = {
    "coins": "🪙 Мои НИТИкоины",
    "rating": "🏆 Рейтинг",
    "hint": "🧩 Подсказка",
    "friday": "🍑 Пошлая пятница",
    "admin_cmds": "🛠️ Команды"
}
