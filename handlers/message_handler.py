from helpers.chat_helpers import handle_character_characteristics, handle_character_name, handle_make_character, handle_start, handle_character_age, handle_character_body, handle_chat_message
from utils.telegram_api import send_message
from helpers.setup_helpers import reset_json_data, get_json_data, update_json_data, set_state, get_state


def handle_message(message):

    chat_id = message["chat"]["id"]
    text = message.get("text")
    json_data = get_json_data()
    character_name = json_data.get('character_name')
    character_age = json_data.get('character_age')
    character_body = json_data.get('character_body')
    character_characteristics = json_data.get('character_characteristics')

    state = get_state()

    if text and (text.startswith("/reset")):
        reset_json_data()
        send_message(chat_id, "Session reset. Send /start to begin again.")
        return

    # Start command
    if text and (text.startswith("/start")):
        handle_start(message)
        return
    
    if text and text.lower() == "/setup":
        handle_make_character(message)
        return
    
    if character_name and character_age and character_body and character_characteristics:
        handle_chat_message(message)
        return
    

    send_message(chat_id, "Send /start to begin. Send /setup to create your character. Send /reset to start over.")


def handle_callback(callback):

    message = callback["message"]
    data = callback["data"]

    state = get_state()

    # NAME SELECTION
    if state == "AWAITING_CHARACTER_NAME":
        handle_character_name(message, data)
        return
    
    if state == "SELECT_AGE":
        handle_character_age(message, data)
        return
    
    if state == "SELECT_BODY":
        handle_character_body(message, data)
        return
    
    if state == "SELECT_CHARACTERISTICS":
        handle_character_characteristics(message, data)
        return
    
    send_message(message["chat"]["id"], "Unknown action. Please follow the prompts.")


