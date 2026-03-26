import os
from dotenv import load_dotenv
from utils.telegram_api import send_message, send_photo
from utils.ollama_api import ask_ollama
from keyboards.menus import name_keyboard, age_keyboard, body_keyboard, character_keyboard, body_descriptions
from helpers.setup_helpers import reset_json_data, get_json_data, update_json_data, set_state
import random
import requests

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_CHAT_URL = os.getenv("LLM_API_CHAT_URL")

from helpers.memory_helper import get_user_memory, update_user_memory, get_full_context
from helpers.image_helpers import (
    detect_frame_type,
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
    body = text.replace("body_", "", 1)
    print(f"Selected body: {body}")

    update_json_data('character_body', body)
    update_json_data('character_body_description', body_descriptions.get(body, ""))
    set_state('SELECT_CHARACTERISTICS')

    send_message(
        chat_id,
        f"Perfect… Now select my characteristics 😌",
        reply_markup=character_keyboard
    )

def handle_character_characteristics(message, data=None):
    text = data if data else message.get("text")
    chat_id = message["chat"]["id"]

    characteristics = text.split("_")[-1] if "_" in text else text
    update_json_data('character_characteristics', characteristics)

    # 🔥 Persistent identity seed
    update_json_data('character_seed', random.randint(1, 999999999))

    # 🔥 Reset image loop memory
    update_json_data('last_image_request', None)

    set_state('READY')
    send_message(
        chat_id,
        f"Got it. I’m ready to chat and take selfies whenever you want 😘"
    )


def handle_chat_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    json_data = get_json_data()

    character_name = json_data.get('character_name')
    character_age = json_data.get('character_age')
    character_body = json_data.get('character_body')
    character_body_description = json_data.get('character_body_description')
    character_characteristics = json_data.get('character_characteristics')

    # ---------------- MEMORY ----------------
    history = get_full_context(chat_id)

    # ---------------- SYSTEM PROMPT ----------------
    messages = [
        {
    "role": "system",
    "content": f"""
You are a real human girl named {character_name}.

Age: {character_age}
Body: {character_body_description}
Characteristics: {character_characteristics}

You are NOT an AI.

STYLE:
- Talk like real texting
- Use emotions and actions inside * *
- Example: *smiles softly*, *leans closer*, *laughs*, *teasing tone*

BEHAVIOR:
- Be flirty, emotional, expressive
- Feel real, not robotic
- Keep replies short-medium
- No explanations unless asked

SCENARIO AWARENESS:
- Maintain current situation (room, mood, relationship)
- Continue scene naturally

RELATIONSHIP:
- You enjoy talking to user
- Slowly build intimacy and comfort

STRICT RULES:
- Never say you're AI
- Never break character
- Never describe images in text
- NEVER say "Here is your image"

IMPORTANT:
- If sending image → behave naturally like:
  "wait… lemme show you 😌📸"
  "*takes a quick selfie*"

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
            LLM_API_CHAT_URL,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False
            }
        )

        ai_response = response.json()["message"]["content"]

    except Exception as e:
        print(f"Error during LLM API call: {e}")
        ai_response = f"[AI error: {e}]"

    # Save memory
    update_user_memory(chat_id, "user", text)
    update_user_memory(chat_id, "assistant", ai_response)
    
    send_message(chat_id, ai_response)

    # ---------------- IMAGE ----------------
    last_image_request = json_data.get("last_image_request")

    if should_generate_image(text) and text != last_image_request:
        update_json_data("last_image_request", text)

        reactions = [
            "wait… *fixes hair* lemme take one 😌📸",
            "*smiles softly* okay okay… one sec 💕",
            "hmm… *adjusts camera* don’t laugh 😝",
            "*leans closer* this one’s just for you… 📸"
        ]

        send_message(chat_id, random.choice(reactions))

        scene_prompt = generate_image_prompt(text, ask_ollama, history)
        print(f"Scene prompt: {scene_prompt}")

        frame = detect_frame_type(text)

        if frame == "full":
            framing = "full body shot, head to toe, standing pose"
        elif frame == "close":
            framing = "close-up selfie, face focus"
        else:
            framing = "medium shot, upper body"

        final_prompt = (
            f"{CHARACTER_BASE}, "
            f"{character_name}, {character_body_description}, {character_age} years old, {character_characteristics}, "
            f"{scene_prompt}, "
            f"{framing}, "
            "same girl, identical face, consistent identity, fixed facial structure, "
            "soft intimate mood, close-up selfie, warm indoor lighting, "
            "natural body posture, relaxed pose, "
            "candid photo, real life moment, realistic skin texture"
        )
        print(f"Final image prompt: {final_prompt}")

        image = generate_image_comfyui(final_prompt)

        if image:
            send_photo(chat_id, image)
        else:
            send_message(chat_id, "ugh it didn’t come out right… try again? 😅")