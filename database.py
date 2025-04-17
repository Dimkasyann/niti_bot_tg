import json
from datetime import datetime
from pathlib import Path

def load_puzzles():
    if not Path('puzzles.json').exists():
        return {}
    with open('puzzles.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_puzzle(date: str, question: str, answer: str, hint: str):
    data = load_puzzles()
    data[date] = {
        "question": question,
        "answer": answer,
        "hint": hint,
        "is_friday": datetime.strptime(date, "%Y-%m-%d").weekday() == 4
    }
    with open('puzzles.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_today_puzzle():
    today = datetime.now().strftime("%Y-%m-%d")
    return load_puzzles().get(today)

def update_scores(user_id: int, coins: int):
    try:
        with open('user_scores.json', 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data[str(user_id)] = data.get(str(user_id), 0) + coins
            f.seek(0)
            json.dump(data, f, ensure_ascii=False)
    except FileNotFoundError:
        with open('user_scores.json', 'w', encoding='utf-8') as f:
            json.dump({str(user_id): coins}, f, ensure_ascii=False)
