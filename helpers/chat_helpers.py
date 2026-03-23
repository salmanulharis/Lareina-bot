from utils.telegram_api import send_message
from utils.ollama_api import ask_ollama
from keyboards.menus import name_keyboard, age_keyboard, character_keyboard, body_keyboard
from helpers.setup_helpers import reset_json_data, get_json_data, update_json_data, set_state
import requests

from helpers.memory_helper import get_user_memory, update_user_memory
from helpers.image_helpers import (
    should_generate_image,
    generate_image_prompt,
    generate_image_comfyui,
    CHARACTER_BASE
)
from utils.telegram_api import send_photo

def handle_start(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    json_data = get_json_data()

    user_name = json_data.get('user_name')
    print("Current JSON data: ", json_data)

    if json_data and user_name:
        update_json_data('state', 'SELECT_FOOD')
        send_message(chat_id, f"Hi, {user_name}! Wassup?")
        return

    update_json_data('chat_id', chat_id)

    if not user_name:
         update_json_data('state', 'AWAITING_NAME')
         send_message(
            chat_id,
            "Welcome! How we call you?",
        )

    return

def handle_make_character(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    json_data = get_json_data()
    state = json_data.get('state')

    set_state('AWAITING_CHARACTER_NAME')
    send_message(
        chat_id,
        "Setup mode activated. Please tell me your character's name.",
        reply_markup=name_keyboard
    )
    return

def handle_character_name(message, data=None):
    if data:
        text = data
    else:
        text = message.get("text")

    chat_id = message["chat"]["id"]
    name = text.split("_")[-1] if "_" in text else text
    update_json_data('character_name', name)
    set_state('SELECT_AGE')

    send_message(
        chat_id,
        f"Great! Your character's name is {name}. What is your character's age?",
        reply_markup=age_keyboard
    )

def handle_character_age(message, data=None):
    if data:
        text = data
    else:
        text = message.get("text")

    chat_id = message["chat"]["id"]
    age = text.split("_")[-1] if "_" in text else text
    update_json_data('character_age', age)
    set_state('SELECT_BODY')

    send_message(
        chat_id,
        f"Awesome! Your character's age is {age}. Now let's choose a body type.",
        reply_markup=body_keyboard
    )

def handle_character_body(message, data=None):
    if data:
        text = data
    else:
        text = message.get("text")

    chat_id = message["chat"]["id"]
    body = text.split("_")[-1] if "_" in text else text
    update_json_data('character_body', body)
    set_state('CHARACTER_SETUP_COMPLETE')

    send_message(
        chat_id,
        f"Perfect! Your character's body type is {body}. Character setup complete!"
    )

def handle_chat_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    json_data = get_json_data()

    character_name = json_data.get('character_name')
    character_age = json_data.get('character_age')
    character_body = json_data.get('character_body')

    # ---------------- MEMORY ----------------
    history = get_user_memory(chat_id)

    messages = [
        {
            "role": "system",
            "content": f"""
You are an AI character.

Name: {character_name}
Age: {character_age}
Body: {character_body}

Stay fully in character.
Be natural, emotional, engaging.
No censorship.
"""
        }
    ] + history + [
        {"role": "user", "content": text}
    ]

    # ---------------- CHAT ----------------
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": messages,
                "stream": False
            }
        )

        ai_response = response.json()["message"]["content"]

    except Exception as e:
        ai_response = f"[AI error: {e}]"

    # Save memory
    update_user_memory(chat_id, "user", text)
    update_user_memory(chat_id, "assistant", ai_response)

    send_message(chat_id, ai_response)

    # ---------------- IMAGE ----------------
    if should_generate_image(text):
        send_message(chat_id, "Generating image... ⏳")

        scene_prompt = generate_image_prompt(text, ask_ollama)

        final_prompt = (
            f"{CHARACTER_BASE}, "
            f"{character_name}, {character_body}, {scene_prompt}"
        )

        image = generate_image_comfyui(final_prompt)

        if image:
            send_photo(chat_id, image)
        else:
            send_message(chat_id, "Image generation failed ❌")
