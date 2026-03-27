# handlers/callback_handler.py — Routes Telegram inline keyboard callback queries.
# Maps current session state to the correct setup step handler.

from memory.session_store import get_state
from services.setup_service import (
    save_character_name,
    save_character_age,
    save_character_body,
    save_character_traits,
)
from utils.telegram import send_message


# Maps state → handler function
_STATE_HANDLERS = {
    "AWAITING_CHARACTER_NAME": save_character_name,
    "SELECT_AGE":              save_character_age,
    "SELECT_BODY":             save_character_body,
    "SELECT_CHARACTERISTICS":  save_character_traits,
}


def handle_callback(callback: dict):
    message = callback["message"]
    data = callback["data"]
    state = get_state()

    handler = _STATE_HANDLERS.get(state)

    if handler:
        handler(message, data)
    else:
        send_message(message["chat"]["id"], "Unknown action. Please follow the prompts.")