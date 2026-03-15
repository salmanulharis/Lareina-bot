from utils.telegram_api import send_message
from keyboards.menus import food_menu, drink_menu
from services.user_session import user_states, user_data


def handle_message(message):

    chat_id = message["chat"]["id"]
    text = message.get("text")

    state = user_states.get(chat_id)

    # Start command
    if text and (text.startswith("/start") or text.lower().startswith("hi")):

        user_states[chat_id] = "SELECT_FOOD"
        user_data[chat_id] = {}

        send_message(
            chat_id,
            "Welcome! Choose your food:",
            reply_markup=food_menu()
        )

        return

    # Address input step
    if state == "ENTER_ADDRESS":

        user_data[chat_id]["address"] = text

        food = user_data[chat_id]["food"]
        drink = user_data[chat_id]["drink"]
        address = user_data[chat_id]["address"]

        response = f"""
Order summary:

Food: {food}
Drink: {drink}
Address: {address}
"""

        send_message(chat_id, response)

        # reset state
        user_states.pop(chat_id, None)

        return

    send_message(chat_id, "Send /start to begin.")


def handle_callback(callback):

    chat_id = callback["message"]["chat"]["id"]
    data = callback["data"]

    state = user_states.get(chat_id)

    # FOOD SELECTION
    if state == "SELECT_FOOD":

        user_data[chat_id]["food"] = data
        user_states[chat_id] = "SELECT_DRINK"

        send_message(
            chat_id,
            "Choose your drink:",
            reply_markup=drink_menu()
        )

        return

    # DRINK SELECTION
    if state == "SELECT_DRINK":

        user_data[chat_id]["drink"] = data
        user_states[chat_id] = "ENTER_ADDRESS"

        send_message(chat_id, "Enter your delivery address:")

        return