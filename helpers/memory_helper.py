import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        # create fresh file
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
        return {}

    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    except json.JSONDecodeError:
        print("⚠️ Memory corrupted → deleting and recreating...")

        try:
            os.remove(MEMORY_FILE)
        except Exception as e:
            print("Failed to delete corrupted file:", e)

        # recreate clean file
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)

        return {}

def save_memory(data):
    temp_file = MEMORY_FILE + ".tmp"

    try:
        # ---------------- LIMIT MEMORY ----------------

        # ✅ Keep only summarized memory
        if "memory" in data:
            data["memory"] = data["memory"][-800:]  # 🔥 hard limit

        # ✅ Keep only last N chat messages
        if "messages" in data and isinstance(data["messages"], list):
            data["messages"] = data["messages"][-10:]  # 🔥 last 10 messages only

        # Optional: clean empty keys
        cleaned_data = {k: v for k, v in data.items() if v}

        # ---------------- SAVE ----------------
        with open(temp_file, "w") as f:
            json.dump(cleaned_data, f, indent=2)

        os.replace(temp_file, MEMORY_FILE)

    except Exception as e:
        print("Error saving memory:", e)

def get_user_memory(chat_id):
    data = load_memory()
    return data.get(str(chat_id), [])

def update_user_memory(chat_id, role, content, max_history=50):
    data = load_memory()

    history = data.get(str(chat_id), [])
    history.append({
        "role": role,
        "content": content
    })

    history = history[-max_history:]
    data[str(chat_id)] = history

    save_memory(data)

def get_full_context(chat_id):
    data = load_memory()
    history = data.get(str(chat_id), [])

    # convert to readable story
    context = ""
    for msg in history[-20:]:
        context += f"{msg['role']}: {msg['content']}\n"

    return context