# memory/conversation_store.py — Manages memory.json (chat history + AI summary).
#
# Structure of memory.json:
# {
#   "<chat_id>": {
#     "history": [ {"role": "user"|"assistant", "content": "..."}, ... ],
#     "summary": "AI-generated bullet-point memory of this user"
#   }
# }
#
# History is capped at MAX_CHAT_HISTORY messages per user.
# Summary is capped at MAX_MEMORY_SUMMARY_CHARS characters.

import json
import os
from config.settings import MEMORY_FILE, MAX_CHAT_HISTORY, MAX_MEMORY_SUMMARY_CHARS


# ── Internal read/write ───────────────────────────────────────────────────────

def _read() -> dict:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print(f"[MEMORY] Invalid format (not dict) — resetting file.")
                return {}
            return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"[MEMORY] Read error — resetting: {e}")
        return {}


def _write(data: dict):
    tmp = MEMORY_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, MEMORY_FILE)
    except OSError as e:
        print(f"[MEMORY] Write error: {e}")


def _get_user_bucket(data: dict, chat_id: int) -> dict:
    return data.setdefault(str(chat_id), {"history": [], "summary": ""})


# ── Public API ────────────────────────────────────────────────────────────────

def append_message(chat_id: int, role: str, content: str):
    """Append one message to the user's history. Trims to MAX_CHAT_HISTORY."""
    data = _read()
    bucket = _get_user_bucket(data, chat_id)

    bucket["history"].append({"role": role, "content": content})
    bucket["history"] = bucket["history"][-MAX_CHAT_HISTORY:]

    _write(data)


def get_recent_history(chat_id: int) -> list[dict]:
    """Return the stored recent message history for this user."""
    data = _read()
    return data.get(str(chat_id), {}).get("history", [])


def get_memory_summary(chat_id: int) -> str:
    """Return the AI-generated memory summary for this user."""
    data = _read()
    return data.get(str(chat_id), {}).get("summary", "")


def update_memory_summary(chat_id: int, summary: str):
    """Overwrite the memory summary. Trims to MAX_MEMORY_SUMMARY_CHARS."""
    data = _read()
    bucket = _get_user_bucket(data, chat_id)
    bucket["summary"] = summary.strip()[:MAX_MEMORY_SUMMARY_CHARS]
    _write(data)


def clear_user_memory(chat_id: int):
    """Delete all history and summary for this user."""
    data = _read()
    data.pop(str(chat_id), None)
    _write(data)