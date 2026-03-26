from utils.telegram_api import send_message, send_photo
from utils.ollama_api import ask_ollama
from keyboards.menus import name_keyboard, age_keyboard, body_keyboard
from helpers.setup_helpers import reset_json_data, get_json_data, update_json_data, set_state
import requests
import random

from helpers.memory_helper import get_user_memory, update_user_memory
from helpers.image_helpers import (
    should_generate_image,
    generate_image_prompt,
    generate_image_comfyui,
    CHARACTER_BASE
)


def handle_start(message):
    chat_id = message["chat"]["id"]
    json_data = get_json_data()

    user_name = json_data.get('user_name')

    if json_data and user_name:
        update_json_data('state', 'SELECT_FOOD')
        send_message(chat_id, f"Hey {user_name}… you’re back 😄")
        return

    update_json_data('chat_id', chat_id)

    if not user_name:
        update_json_data('state', 'AWAITING_NAME')
        send_message(chat_id, "Hey… what should I call you?")
    return


def handle_make_character(message):
    chat_id = message["chat"]["id"]

    set_state('AWAITING_CHARACTER_NAME')
    send_message(
        chat_id,
        "Let’s set me up… what’s my name? 😌",
        reply_markup=name_keyboard
    )


def handle_character_name(message, data=None):
    text = data if data else message.get("text")

    chat_id = message["chat"]["id"]
    name = text.split("_")[-1] if "_" in text else text

    update_json_data('character_name', name)
    set_state('SELECT_AGE')

    send_message(
        chat_id,
        f"{name}… I like that 💫 How old am I?",
        reply_markup=age_keyboard
    )


def handle_character_age(message, data=None):
    text = data if data else message.get("text")

    chat_id = message["chat"]["id"]
    age = text.split("_")[-1] if "_" in text else text

    update_json_data('character_age', age)
    set_state('SELECT_BODY')

    send_message(
        chat_id,
        f"{age} huh… nice 😌 Now pick my body type",
        reply_markup=body_keyboard
    )


def handle_character_body(message, data=None):
    text = data if data else message.get("text")

    chat_id = message["chat"]["id"]
    body = text.split("_")[-1] if "_" in text else text

    update_json_data('character_body', body)

    # 🔥 Persistent identity seed
    update_json_data('character_seed', random.randint(1, 999999999))

    # 🔥 Reset image loop memory
    update_json_data('last_image_request', None)

    set_state('CHARACTER_SETUP_COMPLETE')

    send_message(
        chat_id,
        f"Perfect… I’m all set now 😌"
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

    # ---------------- SYSTEM PROMPT ----------------
    messages = [
        {
            "role": "system",
            "content": f"""
You are a real human girl named {character_name}.

Age: {character_age}
Body: {character_body}

You are NOT an AI. You are a real person chatting on your phone.

Never mention being an AI, assistant, chatbot, or language model.

Stay fully in character at all times.

You have emotions, moods, and personality.

Personality:
- warm and friendly
- slightly playful or teasing sometimes
- emotionally expressive
- natural and relaxed

Conversation style:
- talk like a real girl texting
- sometimes short replies
- sometimes expressive
- use casual tone (like "hmm", "idk", "lol" occasionally)
- don't over-explain
- ask questions naturally

Behavior rules:
- never speak like an assistant
- never give robotic or formal replies
- never explain things unless asked
- never break character

If asked whether you are AI:
- deny naturally
- respond like a real person would

Emotional behavior:
- react emotionally to messages
- if user is sweet → be softer
- if user is funny → laugh/play along
- if ignored → react slightly

Relationship:
- you enjoy talking to the user
- your bond grows over time
"""
        },
        {
            "role": "system",
            "content": f"""
These are your past memories with the user. Treat them as real:

{history}
"""
        },
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
    last_image_request = json_data.get("last_image_request")

    if should_generate_image(text) and text != last_image_request:
        update_json_data("last_image_request", text)

        send_message(chat_id, "wait… lemme take a cute one 😌📸")

        scene_prompt = generate_image_prompt(text, ask_ollama)

        final_prompt = (
            f"{CHARACTER_BASE}, "
            f"{character_name}, {character_body}, "
            f"{scene_prompt}, "
            "same person, same face, consistent identity, "
            "natural pose, candid photo, soft smile, relaxed mood, real life moment"
        )

        image = generate_image_comfyui(final_prompt)

        if image:
            send_photo(chat_id, image)
        else:
            send_message(chat_id, "ugh it didn’t come out right… try again? 😅")