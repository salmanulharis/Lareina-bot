# keyboards/menus.py — All inline keyboard definitions for character setup.
# Each keyboard is pre-built at import time so they're ready to use instantly.

from keyboards.builder import build_inline_keyboard

# ── Character name options ────────────────────────────────────────────────────
_NAMES = {
    "aira": "Aira", "riya": "Riya", "elena": "Elena", "mia": "Mia",
    "nyx": "Nyx", "zara": "Zara", "victoria": "Victoria", "luna": "Luna",
}

# ── Age options ───────────────────────────────────────────────────────────────
_AGES = {
    "18": "18", "20": "20", "22": "22", "24": "24",
    "26": "26", "28": "28", "30": "30",
}

# ── Personality trait options ─────────────────────────────────────────────────
_TRAITS = {
    "sweet": "Sweet & Caring",
    "flirty": "Flirty & Playful",
    "smart": "Intelligent & Mature",
    "gamer": "Gamer Girl",
    "mysterious": "Mysterious & Quiet",
    "funny": "Funny & Chaotic",
    "bossy": "Bossy / Dominant",
    "shy": "Shy & Innocent",
}

# ── Body type options ─────────────────────────────────────────────────────────
_BODY_TYPES = {
    "petite_curvy": "Petite & Curvy",
    "slim_thick": "Slim Thick",
    "hourglass": "Hourglass Figure",
    "fit_curvy": "Fit & Curvy",
    "lean_athletic": "Lean Athletic",
    "voluptuous": "Voluptuous",
    "tall_model": "Tall Model-like",
    "perfect_curvy_blonde": "Perfect Curvy Blonde",
}

# ── Body type descriptions (used in image prompts) ────────────────────────────
BODY_DESCRIPTIONS = {
    "petite_curvy": "short height, compact frame, soft curves, proportionate bust and hips, youthful appearance",
    "slim_thick": "slim waist, fuller hips, rounded curves, toned legs, balanced proportions",
    "hourglass": "defined waist, balanced bust and hips, natural symmetry, classic feminine proportions",
    "fit_curvy": "toned body, visible fitness, soft curves, firm shape, athletic yet feminine",
    "lean_athletic": "lean muscle tone, light definition, smaller curves, sporty and energetic",
    "voluptuous": "fuller body, soft curves, wider hips, fuller bust, smooth rounded proportions",
    "tall_model": "tall height, long legs, slim body, elegant posture, fashion model proportions",
    "perfect_curvy_blonde": "hourglass body, full bust, wide hips, defined waist, long blonde hair, soft waves",
}

# ── Pre-built keyboards ───────────────────────────────────────────────────────
name_keyboard      = build_inline_keyboard(_NAMES,      columns=2, callback_prefix="name")
age_keyboard       = build_inline_keyboard(_AGES,       columns=3, callback_prefix="age")
character_keyboard = build_inline_keyboard(_TRAITS,     columns=2, callback_prefix="char")
body_keyboard      = build_inline_keyboard(_BODY_TYPES, columns=2, callback_prefix="body")