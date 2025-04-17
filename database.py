# database.py
import json

def save_user_data(user_id, coins):
    data = {}
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        pass
    data[user_id] = coins
    with open('data.json', 'w') as f:
        json.dump(data, f)
