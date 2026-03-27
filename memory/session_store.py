# memory/session_store.py — Manages data.json (session state + character config).
# Keeps character info, current state, and one-shot flags like last_image_request.

import json
import os
from config.settings import SESSION_FILE


# ── Internal read/write ───────────────────────────────────────────────────────

def _read() -> dict:
    if not os.path.exists(SESSION_FILE):
        return {}
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[SESSION] Read error: {e}")
        return {}


def _write(data: dict):
    tmp = SESSION_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, SESSION_FILE)
    except OSError as e:
        print(f"[SESSION] Write error: {e}")


# ── Public API ────────────────────────────────────────────────────────────────

def get_session() -> dict:
    return _read()


def update_session(key: str, value):
    data = _read()
    data[key] = value
    _write(data)


def reset_session():
    """Wipe session data completely (used by /reset)."""
    _write({})


def get_state() -> str | None:
    return _read().get("state")


def set_state(state: str):
    update_session("state", state)