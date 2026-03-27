# utils/telegram.py — Thin wrappers around the Telegram Bot API.
# All outbound communication to Telegram goes through here.

import requests
from config.settings import TELEGRAM_API_BASE


def send_message(chat_id: int, text: str, reply_markup: str | None = None):
    """Send a text message to a Telegram chat."""
    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        res = requests.post(url, json=payload, timeout=10)
        if not res.ok:
            print(f"[TELEGRAM] sendMessage failed {res.status_code}: {res.text[:200]}")
    except requests.RequestException as e:
        print(f"[TELEGRAM] sendMessage error: {e}")


def send_photo(chat_id: int, image_bytes: bytes):
    """Send a photo (raw bytes) to a Telegram chat."""
    url = f"{TELEGRAM_API_BASE}/sendPhoto"

    try:
        res = requests.post(
            url,
            data={"chat_id": chat_id},
            files={"photo": ("image.png", image_bytes, "image/png")},
            timeout=30,
        )
        if not res.ok:
            print(f"[TELEGRAM] sendPhoto failed {res.status_code}: {res.text[:200]}")
    except requests.RequestException as e:
        print(f"[TELEGRAM] sendPhoto error: {e}")