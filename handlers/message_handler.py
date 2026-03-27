# handlers/message_handler.py — Routes incoming Telegram text messages.
# Checks session state and delegates to the right service.

from memory.session_store import get_session, reset_session, get_state
from services.setup_service import start_setup, begin_character_creation
from services.chat_service import handle_chat
from utils.telegram import send_message


def handle_message(message: dict):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if not text:
        return

    # ── Hard commands — always available ─────────────────────────────────────
    if text.startswith("/reset"):
        reset_session()
        send_message(chat_id, "Session reset. Send /start to begin again.")
        return

    if text.startswith("/start"):
        start_setup(message)
        return

    if text.lower() == "/setup":
        begin_character_creation(message)
        return

    # ── Normal chat — only if character is fully configured ──────────────────
    session = get_session()
    character_ready = all([
        session.get("character_name"),
        session.get("character_age"),
        session.get("character_body"),
        session.get("character_characteristics"),
    ])

    if character_ready:
        handle_chat(message)
        return

    send_message(
        chat_id,
        "Send /start to begin. Send /setup to create your character. Send /reset to start over."
    )