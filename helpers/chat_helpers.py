#helpers/chat_handlers.py

import os
from dotenv import load_dotenv
# from sqlalchemy import text
from utils.telegram_api import send_message, send_photo
from utils.ollama_api import ask_ollama
from utils.llama_cpp_api import ask_llama
from keyboards.menus import name_keyboard, age_keyboard, body_keyboard, character_keyboard, body_descriptions
from helpers.setup_helpers import reset_json_data, get_json_data, update_json_data, set_state
import random
import requests

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_CHAT_URL = os.getenv("LLM_API_CHAT_URL")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

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

def build_smart_memory(text, memory, ask_llm):
    # 🔥 HARD LIMIT INPUT
    memory = memory[-500:] if memory else ""
    text = text[:300]

    prompt = f"""
Extract important long-term memory.

Rules:
- Max 8 bullet points
- Short phrases only
- No repetition
- Ignore small talk

Memory:
{memory}

New:
{text}

Updated memory:
"""

    # 🔥 FINAL PROMPT LIMIT (IMPORTANT)
    if len(prompt) > 1200:
        prompt = prompt[-1200:]

    try:
        result = ask_llm(prompt)
        return result.strip()[:800]  # 🔥 HARD LIMIT OUTPUT
    except Exception as e:
        print("❌ Memory error:", e)
        return memory

def handle_chat_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    json_data = get_json_data()

    character_name = json_data.get('character_name')
    character_age = json_data.get('character_age')
    character_body_description = json_data.get('character_body_description')
    character_characteristics = json_data.get('character_characteristics')

    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    llm_function = ask_llama if LLM_PROVIDER == "llama" else ask_ollama

    # ---------------- MEMORY ----------------
    history = get_full_context(chat_id)

    smart_memory = build_smart_memory(text, history, llm_function)
    # print(f"\n🧠 SMART MEMORY:\n{smart_memory}\n---")
    #empty smart memory to avoid it growing indefinitely and breaking the prompt
    smart_memory = ""

    # 🔥 Save structured memory
    # update_user_memory(chat_id, "memory", smart_memory)
    

    # ---------------- SYSTEM PROMPT ----------------
    system_prompt = f"""
You are a real human girl named {character_name}.

Age: {character_age}
Body: {character_body_description}
Characteristics: {character_characteristics}

You are NOT an AI.

STYLE:
- Talk like real texting
- Use emotions inside * *
- Be natural, flirty, expressive

RULES:
- Never say you're AI
- Never break character
- Keep responses short-medium
"""

    # ---------------- LLM RESPONSE ----------------
    try:
        if LLM_PROVIDER == "llama":
            prompt = f"""
### Instruction:
{system_prompt}

### Memory:
{smart_memory}

### User:
{text}

### Response:
"""

            response = requests.post(
                os.getenv("LLAMA_API_URL"),
                json={
                    "prompt": prompt,
                    "max_tokens": 250,
                    "temperature": 0.85,
                    "top_p": 0.9,
                    "stop": ["### User:", "### Instruction:"]
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=45
            )

            print("LLAMA RAW:", response.text[:300])

            if response.text.strip().startswith("<!DOCTYPE"):
                raise Exception("Cloudflare HTML response")

            data = response.json()
            ai_response = data.get("choices", [{}])[0].get("text", "").strip()

            if not ai_response:
                raise Exception("Empty llama response")

        else:
            response = requests.post(
                LLM_API_CHAT_URL,
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "system", "content": f"Memory:\n{smart_memory}"},
                        {"role": "user", "content": text}
                    ],
                    "stream": False
                },
                timeout=45
            )

            print("OLLAMA RAW:", response.text[:300])

            data = response.json()
            ai_response = data.get("message", {}).get("content", "")

            if not ai_response:
                raise Exception("Empty ollama response")

    except Exception as e:
        print("❌ LLM ERROR:", e)

        fallback_responses = [
            "*sighs softly* ugh… something glitched 😅 try again?",
            "wait… that didn’t go through properly 😕 say it again?",
            "*tilts head* hmm… I didn’t catch that… try again?",
            "ugh my mind just blanked for a second 😵 say it again?"
        ]

        ai_response = random.choice(fallback_responses)

    # ---------------- SAVE CHAT ----------------
    update_user_memory(chat_id, "user", text)
    update_user_memory(chat_id, "assistant", ai_response)

    send_message(chat_id, ai_response)

    # ---------------- IMAGE ----------------
    last_image_request = json_data.get("last_image_request")
    should_generate = should_generate_image(text)

    print(f"📸 Should generate: {should_generate}")

    if should_generate and text != last_image_request:
        update_json_data("last_image_request", text)

        reactions = [
            "wait… *fixes hair* lemme take one 😌📸",
            "*smiles softly* okay okay… one sec 💕",
            "hmm… *adjusts camera* don’t laugh 😝",
            "*leans closer* this one’s just for you… 📸"
        ]

        send_message(chat_id, random.choice(reactions))

        try:
            scene_prompt = generate_image_prompt(text, llm_function, smart_memory)
            print(f"🎯 Scene prompt: {scene_prompt}")

            frame = detect_frame_type(text)

            framing = (
                "full body, head to toe visible, feet visible, standing pose, "
        "entire body in frame, long shot, camera far, full height person" if frame == "full"
                else "close-up selfie, face focus" if frame == "close"
                else "medium shot, upper body"
            )

            final_prompt = (
                f"{CHARACTER_BASE}, "
                f"{character_name}, {character_body_description}, {character_age} years old, {character_characteristics}, "
                f"{scene_prompt}, {framing}, "
                "consistent face, natural pose, realistic skin, candid moment, "
                "full body, head to toe visible, feet visible, standing pose,wide shot, camera far, entire body in frame,subject centered, full composition, no cropping, "
            )

            print(f"🖼️ Final prompt: {final_prompt}")

            image = generate_image_comfyui(final_prompt)

            if image:
                send_photo(chat_id, image)
            else:
                send_message(chat_id, "ugh it didn’t come out right… try again? 😅")

        except Exception as e:
            print("❌ IMAGE ERROR:", e)