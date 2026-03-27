# utils/llm.py — Unified LLM interface.
# ask_llm() accepts the prompt dict from any prompt builder and routes to
# the correct backend (ollama or llama.cpp) based on LLM_PROVIDER setting.
# Returns a plain string response, or None on failure — never raises.

import requests
import json
from config.settings import (
    get_llm_provider,
    MODEL_NAME,
    OLLAMA_API_URL,
    OLLAMA_CHAT_URL,
    LLAMA_API_URL,
    LLM_TIMEOUT_SECONDS,
    LLM_MAX_TOKENS,
)


def ask_llm(prompt: dict) -> str | None:
    """
    prompt: { "mode": "chat" | "completion", "payload": <messages list or string> }

    Returns the model's text response, or None on any error.
    Errors are logged to console only — never surfaced to the user.
    """
    if not prompt or "payload" not in prompt:
        print("[LLM] ask_llm called with invalid prompt dict")
        return None

    try:
        if get_llm_provider() == "llama":
            return _ask_llama(prompt)
        else:
            return _ask_ollama(prompt)
    except Exception as e:
        print(f"[LLM] Unexpected error: {e}")
        return None


# ── Ollama backend ────────────────────────────────────────────────────────────

def _ask_ollama(prompt: dict) -> str | None:
    mode = prompt["mode"]
    payload_data = prompt["payload"]

    if mode == "chat":
        # /api/chat — takes messages list
        if not OLLAMA_CHAT_URL:
            print("[LLM] OLLAMA_CHAT_URL not set")
            return None

        body = {
            "model": MODEL_NAME,
            "messages": payload_data,
            "stream": False,
        }
        res = requests.post(OLLAMA_CHAT_URL, json=body, timeout=LLM_TIMEOUT_SECONDS)
        res.raise_for_status()
        data = res.json()
        reply = data.get("message", {}).get("content", "").strip()

    else:
        # /api/generate — takes a single prompt string
        if not OLLAMA_API_URL:
            print("[LLM] OLLAMA_API_URL not set")
            return None

        body = {
            "model": MODEL_NAME,
            "prompt": payload_data,
            "stream": False,
        }
        res = requests.post(OLLAMA_API_URL, json=body, timeout=LLM_TIMEOUT_SECONDS)
        res.raise_for_status()
        data = res.json()
        reply = data.get("response", "").strip()

    if not reply:
        print(f"[LLM] Ollama returned empty response (mode={mode})")
        return None

    return reply


# ── llama.cpp backend ─────────────────────────────────────────────────────────

def _ask_llama(prompt: dict) -> str | None:
    payload_data = prompt.get("payload")

    if not LLAMA_API_URL:
        print("[LLM] LLAMA_API_URL not set")
        return None

    try:
        # =========================
        # BUILD PROMPT (IMPORTANT)
        # =========================
        if isinstance(payload_data, list):
            # convert chat → text prompt
            formatted = ""
            for msg in payload_data[-6:]:  # limit memory
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                formatted += f"{role}: {content}\n"

            formatted += "Assistant:"
        else:
            formatted = str(payload_data)

        body = {
            "model": MODEL_NAME,
            "prompt": formatted,
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": 0.85,
            "top_p": 0.9,
            "stream": False
        }

        # 🔥 DEBUG
        print("[LLAMA REQUEST]", json.dumps(body, indent=2))

        res = requests.post(
            LLAMA_API_URL,  # MUST be /v1/completions
            json=body,
            timeout=120
        )

        # Cloudflare HTML check
        if res.text.strip().startswith("<!DOCTYPE"):
            print("[LLM] Cloudflare HTML error page")
            return None

        res.raise_for_status()
        data = res.json()

        reply = data.get("choices", [{}])[0].get("text", "").strip()

        if not reply:
            print("[LLM] Empty response", data)
            return None

        return reply

    except requests.exceptions.HTTPError as e:
        print(f"[LLM HTTP ERROR] {e}")
        try:
            print("[LLM RESPONSE BODY]", res.text)
        except:
            pass
        return None

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return None

# def _ask_llama(prompt: dict) -> str | None:
#     mode = prompt["mode"]
#     payload_data = prompt["payload"]

#     if not LLAMA_API_URL:
#         print("[LLM] LLAMA_API_URL not set")
#         return None

#     if mode == "chat":
#         # /v1/chat/completions — takes messages list
#         body = {
#             "model": MODEL_NAME,
#             "messages": payload_data,
#             "temperature": 0.85,
#             "top_p": 0.9,
#             "max_tokens": LLM_MAX_TOKENS,
#             "stream": False,
#             "stop": ["### User:", "### Instruction:"],
#         }
#         res = requests.post(LLAMA_API_URL, json=body, timeout=LLM_TIMEOUT_SECONDS)

#         if res.text.strip().startswith("<!DOCTYPE"):
#             print("[LLM] llama.cpp returned HTML — likely a Cloudflare error page")
#             return None

#         res.raise_for_status()
#         data = res.json()
#         reply = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

#     else:
#         # /v1/completions — takes a single prompt string
#         body = {
#             "prompt": payload_data,
#             "max_tokens": LLM_MAX_TOKENS,
#             "temperature": 0.85,
#             "top_p": 0.9,
#             "stream": False,
#             "stop": ["### User:", "### Instruction:"],
#         }
#         res = requests.post(LLAMA_API_URL, json=body, timeout=LLM_TIMEOUT_SECONDS)

#         if res.text.strip().startswith("<!DOCTYPE"):
#             print("[LLM] llama.cpp returned HTML — likely a Cloudflare error page")
#             return None

#         res.raise_for_status()
#         data = res.json()
#         reply = data.get("choices", [{}])[0].get("text", "").strip()

#     if not reply:
#         print(f"[LLM] llama.cpp returned empty response (mode={mode})")
#         return None

#     return reply