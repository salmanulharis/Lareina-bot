# services/chat_service.py — Core chat pipeline.
# Builds prompt → calls LLM → splits long replies → triggers image if requested.

import random
from memory.session_store import get_session, update_session
from memory.conversation_store import (
    append_message,
    get_recent_history,
    get_memory_summary,
    update_memory_summary,
)
from prompts.chat_prompt import build_chat_prompt
from prompts.memory_prompt import build_memory_summary_prompt
from services.image_service import handle_image_request, should_request_image
from utils.llm import ask_llm
from utils.telegram import send_message


# Max characters before a reply is split into multiple messages
_SPLIT_THRESHOLD = 320


def handle_chat(message: dict):
    chat_id = message["chat"]["id"]
    user_text = message.get("text", "").strip()

    if not user_text:
        return

    session = get_session()

    # ── Build context ─────────────────────────────────────────────────────────
    recent_history = get_recent_history(chat_id)
    memory_summary = get_memory_summary(chat_id)

    prompt_payload = build_chat_prompt(
        session=session,
        user_text=user_text,
        recent_history=recent_history,
        memory_summary=memory_summary,
    )

    # ── Call LLM ──────────────────────────────────────────────────────────────
    ai_reply = ask_llm(prompt_payload)

    if not ai_reply:
        print(f"[CHAT] Empty LLM reply for chat_id={chat_id}")
        return  # Fail silently — no looping, no fallback spam

    # ── Save conversation ─────────────────────────────────────────────────────
    append_message(chat_id, role="user", content=user_text)
    append_message(chat_id, role="assistant", content=ai_reply)

    # ── Async memory compression (best-effort, non-blocking) ──────────────────
    _try_compress_memory(chat_id, recent_history, user_text, ai_reply)

    # ── Send reply (split if long) ────────────────────────────────────────────
    _send_reply(chat_id, ai_reply)

    # ── Image generation (only if user asked, only once per unique request) ───
    if should_request_image(user_text):
        last = session.get("last_image_request")
        if user_text != last:
            update_session("last_image_request", user_text)
            handle_image_request(chat_id, user_text, session, memory_summary)


def _send_reply(chat_id: int, text: str):
    """Split a long reply at sentence boundaries and send as multiple messages."""
    if len(text) <= _SPLIT_THRESHOLD:
        send_message(chat_id, text)
        return

    parts = _split_at_sentences(text, _SPLIT_THRESHOLD)
    for part in parts:
        part = part.strip()
        if part:
            send_message(chat_id, part)


def _split_at_sentences(text: str, max_len: int) -> list[str]:
    """Split text into chunks ≤ max_len, preferring sentence boundaries."""
    sentences = []
    current = ""

    for char in text:
        current += char
        if char in ".!?\n" and len(current) >= 80:
            sentences.append(current.strip())
            current = ""

    if current.strip():
        sentences.append(current.strip())

    # Group sentences into chunks under max_len
    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) + 1 <= max_len:
            chunk = (chunk + " " + sentence).strip()
        else:
            if chunk:
                chunks.append(chunk)
            chunk = sentence

    if chunk:
        chunks.append(chunk)

    return chunks if chunks else [text[:max_len]]


def _try_compress_memory(chat_id: int, history: list, user_text: str, ai_reply: str):
    """Compress conversation into a running summary — fail silently on error."""
    try:
        existing_summary = get_memory_summary(chat_id)
        summary_prompt = build_memory_summary_prompt(
            existing_summary=existing_summary,
            recent_history=history,
            latest_user=user_text,
            latest_reply=ai_reply,
        )
        new_summary = ask_llm(summary_prompt)
        if new_summary:
            update_memory_summary(chat_id, new_summary)
    except Exception as e:
        print(f"[MEMORY] Compression failed for chat_id={chat_id}: {e}")