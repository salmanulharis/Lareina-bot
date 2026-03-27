# services/setup_service.py — Character creation flow.
# Each function handles one step of the /setup wizard.

import random
from memory.session_store import get_session, set_state, update_session
from keyboards.menus import name_keyboard, age_keyboard, body_keyboard, character_keyboard, BODY_DESCRIPTIONS
from utils.telegram import send_message


def start_setup(message: dict):
    """Handle /start — greet returning user or ask for their name."""
    chat_id = message["chat"]["id"]
    session = get_session()
    user_name = session.get("user_name")

    if user_name:
        send_message(chat_id, f"Hey {user_name}… you're back 😄")
        return

    update_session("chat_id", chat_id)
    set_state("AWAITING_NAME")
    send_message(chat_id, "Hey… what should I call you?")


def begin_character_creation(message: dict):
    """Handle /setup — start the character name selection."""
    chat_id = message["chat"]["id"]
    set_state("AWAITING_CHARACTER_NAME")
    send_message(chat_id, "Let's set me up… what's my name? 😌", reply_markup=name_keyboard)


def save_character_name(message: dict, callback_data: str):
    """Save selected name, move to age selection."""
    chat_id = message["chat"]["id"]
    name = callback_data.split("_")[-1]

    update_session("character_name", name)
    set_state("SELECT_AGE")
    send_message(chat_id, f"{name}… I like that 💫 How old am I?", reply_markup=age_keyboard)


def save_character_age(message: dict, callback_data: str):
    """Save selected age, move to body type selection."""
    chat_id = message["chat"]["id"]
    age = callback_data.split("_")[-1]

    update_session("character_age", age)
    set_state("SELECT_BODY")
    send_message(chat_id, f"{age} huh… nice 😌 Now pick my body type", reply_markup=body_keyboard)


def save_character_body(message: dict, callback_data: str):
    """Save selected body type + description, move to personality selection."""
    chat_id = message["chat"]["id"]
    body_key = callback_data.replace("body_", "", 1)

    update_session("character_body", body_key)
    update_session("character_body_description", BODY_DESCRIPTIONS.get(body_key, ""))
    set_state("SELECT_CHARACTERISTICS")
    send_message(chat_id, "Perfect… Now pick my personality 😌", reply_markup=character_keyboard)


def save_character_traits(message: dict, callback_data: str):
    """Save selected personality traits — character setup complete."""
    chat_id = message["chat"]["id"]
    traits = callback_data.split("_")[-1]

    update_session("character_characteristics", traits)
    update_session("character_seed", random.randint(1, 999_999_999))
    update_session("last_image_request", None)
    set_state("READY")

    send_message(chat_id, "Got it. I'm ready to chat whenever you are 😊")