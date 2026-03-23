import requests
from config import TELEGRAM_API


def send_message(chat_id, text, reply_markup=None):

    url = f"{TELEGRAM_API}/sendMessage"
    print(url)

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    r = requests.post(url, json=payload)

    print("Telegram response:", r.text)

def send_photo(chat_id, image_bytes):
    url = f"{TELEGRAM_API}/sendPhoto"

    files = {
        "photo": ("image.png", image_bytes)
    }

    data = {
        "chat_id": chat_id
    }

    requests.post(url, data=data, files=files)