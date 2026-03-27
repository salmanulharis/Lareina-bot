# prompts/image_prompt.py — Builds the final ComfyUI image generation prompt.
# Combines character description with a scene derived from the user's message.

# Base photographic quality tags applied to every image
_PHOTO_BASE = (
    "RAW photo, ultra realistic, photorealistic, 8k, DSLR, "
    "natural skin texture, visible pores, soft imperfections, "
    "cinematic lighting, soft shadows, realistic highlights, "
    "50mm lens, shallow depth of field, bokeh, "
    "natural expression, relaxed face, subtle emotion, "
    "real human proportions, candid moment"
)

_SCENE_EXTRACTION_INSTRUCTION = """Convert this chat message into a short selfie scene description.
Max 12 words. Describe setting and mood only. No names. No dialogue.

Message: {user_text}

Context: {memory_summary}

Output ONLY the scene (e.g. "sitting on bed, soft morning light, relaxed smile"):"""


def build_image_prompt(
    user_text: str,
    session: dict,
    memory_summary: str,
    ask_llm_fn,
) -> str:
    """Build the full ComfyUI prompt string."""
    scene = _extract_scene(user_text, memory_summary, ask_llm_fn)
    framing = _get_framing(user_text)

    character_name = session.get("character_name", "")
    body_desc = session.get("character_body_description", "")
    age = session.get("character_age", "22")
    traits = session.get("character_characteristics", "sweet")

    parts = [
        _PHOTO_BASE,
        f"{character_name}" if character_name else "",
        body_desc,
        f"{age} years old",
        traits,
        scene,
        framing,
        "consistent face, natural pose, realistic skin, no cropping, full composition",
    ]

    return ", ".join(p for p in parts if p)


def _extract_scene(user_text: str, memory_summary: str, ask_llm_fn) -> str:
    """Ask LLM to extract a short scene description from the user's message."""
    prompt_text = _SCENE_EXTRACTION_INSTRUCTION.format(
        user_text=user_text[:200],
        memory_summary=(memory_summary or "none")[:200],
    )
    try:
        from prompts.chat_prompt import _build_completion_prompt  # noqa: avoid circular at module level
        result = ask_llm_fn({"mode": "completion", "payload": prompt_text})
        scene = (result or "").strip().split("\n")[0][:100]
        return scene if scene else "casual indoor setting, soft light"
    except Exception as e:
        print(f"[IMAGE_PROMPT] Scene extraction failed: {e}")
        return "casual indoor setting, soft light"


def _get_framing(user_text: str) -> str:
    lower = user_text.lower()
    if any(k in lower for k in ["full", "full body", "head to toe", "stand"]):
        return (
            "full body, head to toe visible, feet visible, standing pose, "
            "entire body in frame, long shot, wide angle"
        )
    if any(k in lower for k in ["selfie", "face", "close"]):
        return "close-up selfie, face and shoulders, intimate framing"
    return "medium shot, upper body, waist up, natural framing"