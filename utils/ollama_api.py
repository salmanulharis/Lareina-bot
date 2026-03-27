# utils/ollama_api.py

import os
from dotenv import load_dotenv
import requests

load_dotenv()
OLLAMA_API_URL = os.getenv("LLM_API_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

def ask_ollama(prompt, model=MODEL_NAME):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_API_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "[No response from Ollama]")
