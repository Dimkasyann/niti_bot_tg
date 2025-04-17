import string

def normalize_answer(text: str) -> str:
    return ''.join(ch for ch in text.lower().strip() if ch not in string.punctuation).replace(" ", "")
