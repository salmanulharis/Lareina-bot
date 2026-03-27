# prompts/memory_prompt.py — Builds the prompt used to compress conversation history.
# The LLM reads old summary + recent messages and returns an updated compact summary.

_COMPRESSION_TEMPLATE = """Summarize important facts about this user from the conversation.

Rules:
- Max 8 bullet points
- One short phrase per bullet
- Only long-term relevant facts (name, preferences, topics they care about)
- Skip small talk and one-off comments
- Merge with existing memory — no repetition

Existing memory:
{existing_summary}

Recent conversation:
{recent_turns}

Latest exchange:
User: {latest_user}
You: {latest_reply}

Updated memory (bullet points only):"""


def build_memory_summary_prompt(
    existing_summary: str,
    recent_history: list[dict],
    latest_user: str,
    latest_reply: str,
) -> dict:
    """
    Returns a completion-mode prompt dict for ask_llm().
    Memory compression always uses completion mode — it's not a chat turn.
    """
    recent_turns = _format_history(recent_history[-6:])

    prompt_text = _COMPRESSION_TEMPLATE.format(
        existing_summary=(existing_summary or "None yet.").strip()[:400],
        recent_turns=recent_turns[:400],
        latest_user=latest_user[:200],
        latest_reply=latest_reply[:200],
    )

    return {"mode": "completion", "payload": prompt_text}


def _format_history(history: list[dict]) -> str:
    lines = []
    for entry in history:
        label = "User" if entry.get("role") == "user" else "You"
        lines.append(f"{label}: {entry.get('content', '')[:120]}")
    return "\n".join(lines)