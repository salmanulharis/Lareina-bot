import requests
from config import TELEGRAM_API


def send_message(chat_id, text, reply_markup=None):

    url = f"{TELEGRAM_API}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    r = requests.post(url, json=payload)

    print("Telegram response:", r.text)