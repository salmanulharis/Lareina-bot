# utils/llama_cpp_api.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

LLAMA_API_URL = os.getenv("LLAMA_API_URL")  # http://127.0.0.1:8080/v1/chat/completions
MODEL_NAME = os.getenv("MODEL_NAME")


def ask_llama(prompt, model=MODEL_NAME):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": False
    }

    response = requests.post(LLAMA_API_URL, json=payload)
    response.raise_for_status()

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return "[No response from llama.cpp]"