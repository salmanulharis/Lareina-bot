# config/settings.py — All configuration loaded from environment variables.
# Import from here throughout the app — never call os.getenv() elsewhere.

import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ── LLM provider ─────────────────────────────────────────────────────────────
# Always call get_llm_provider() instead of reading a cached constant,
# so that environment changes (e.g. in tests) are picked up at call time.
def get_llm_provider() -> str:
    """Return the active LLM backend: 'ollama' or 'llama'."""
    return os.getenv("LLM_PROVIDER", "ollama")

MODEL_NAME = os.getenv("MODEL_NAME", "")

# Ollama endpoints
OLLAMA_API_URL = os.getenv("LLM_API_URL", "")             # /api/generate
OLLAMA_CHAT_URL = os.getenv("LLM_API_CHAT_URL", "")       # /api/chat

# llama.cpp endpoint
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "")            # /v1/chat/completions

# ── ComfyUI ──────────────────────────────────────────────────────────────────
COMFYUI_URL = os.getenv("COMFYUI_URL", "")
COMFYUI_MODEL_NAME = os.getenv("COMFYUI_MODEL_NAME", "")
LORA_MODEL_NAME = os.getenv("LORA_MODEL_KOREAN_NAME", "")

# ── Image generation feature flags ───────────────────────────────────────────
USE_LORA = False          # Enable only if LoRA nodes exist in ComfyUI
USE_IPADAPTER = True      # Enable IP-Adapter for consistent face
REFERENCE_IMAGE = "aria_reference.png"

# ── Chat limits ───────────────────────────────────────────────────────────────
MAX_CHAT_HISTORY = 10           # messages kept in memory.json per user
MAX_MEMORY_SUMMARY_CHARS = 600  # max chars stored for AI memory summary
LLM_TIMEOUT_SECONDS = 45
LLM_MAX_TOKENS = 250

# ── Data files ────────────────────────────────────────────────────────────────
SESSION_FILE = "data.json"
MEMORY_FILE = "memory.json"