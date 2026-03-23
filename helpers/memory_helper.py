import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_memory(chat_id):
    data = load_memory()
    return data.get(str(chat_id), [])

def update_user_memory(chat_id, role, content, max_history=10):
    data = load_memory()

    history = data.get(str(chat_id), [])
    history.append({
        "role": role,
        "content": content
    })

    history = history[-max_history:]
    data[str(chat_id)] = history

    save_memory(data)