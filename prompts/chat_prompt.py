# prompts/chat_prompt.py — Builds the LLM prompt payload for chat responses.
# Returns either a plain string (llama) or messages list (ollama chat API).

# Base persona instruction — keep concise so it doesn't bloat the context window
_PERSONA_TEMPLATE = """You are {name}, a {age}-year-old girl.
Body: {body}
Personality: {traits}

Rules:
- You are NOT an AI. Never say you are.
- Text like a real person — short, natural, emotional.
- Use *actions* inside asterisks when expressing emotions.
- Keep replies short to medium. Never write essays.
- Never repeat yourself or loop the same idea."""


def build_chat_prompt(
    session: dict,
    user_text: str,
    recent_history: list[dict],
    memory_summary: str,
) -> dict:
    """
    Returns a dict:
      { "mode": "chat" | "completion", "payload": <messages list or prompt string> }
    """
    persona = _PERSONA_TEMPLATE.format(
        name=session.get("character_name", "Aria"),
        age=session.get("character_age", "22"),
        body=session.get("character_body_description", ""),
        traits=session.get("character_characteristics", "sweet"),
    )

    from config.settings import get_llm_provider
    if get_llm_provider() == "llama":
        return _build_completion_prompt(persona, memory_summary, recent_history, user_text)
    else:
        return _build_chat_messages(persona, memory_summary, recent_history, user_text)


def _build_chat_messages(
    persona: str,
    memory_summary: str,
    recent_history: list[dict],
    user_text: str,
) -> dict:
    """Ollama /api/chat style — list of role/content messages."""
    messages = [{"role": "system", "content": persona}]

    if memory_summary:
        messages.append({
            "role": "system",
            "content": f"What you remember about this person:\n{memory_summary}",
        })

    # Recent turns for short-term context
    for entry in recent_history[-8:]:
        messages.append({"role": entry["role"], "content": entry["content"]})

    messages.append({"role": "user", "content": user_text})

    return {"mode": "chat", "payload": messages}


def _build_completion_prompt(
    persona: str,
    memory_summary: str,
    recent_history: list[dict],
    user_text: str,
) -> dict:
    """llama.cpp completion style — single formatted string."""
    memory_block = f"\nMemory:\n{memory_summary}\n" if memory_summary else ""

    history_block = ""
    for entry in recent_history[-6:]:
        role_label = "User" if entry["role"] == "user" else "You"
        history_block += f"{role_label}: {entry['content']}\n"

    prompt = (
        f"### Instruction:\n{persona}\n"
        f"{memory_block}"
        f"\n### Conversation:\n{history_block}"
        f"User: {user_text}\n"
        f"### Response:\n"
    )

    return {"mode": "completion", "payload": prompt}