from utils.keyboard_helper import create_menu

options = {
    "names": {
        "aira": "Aira",
        "riya": "Riya",
        "elena": "Elena",
        "mia": "Mia",
        "nyx": "Nyx",
        "zara": "Zara",
        "victoria": "Victoria",
        "luna": "Luna"
    },

    "ages": {
        "18": 18,
        "20": 20,
        "22": 22,
        "24": 24,
        "26": 26,
        "28": 28,
        "30": 30
    },

    "characters": {
        "sweet": "Sweet & Caring",
        "flirty": "Flirty & Playful",
        "smart": "Intelligent & Mature",
        "gamer": "Gamer Girl",
        "mysterious": "Mysterious & Quiet",
        "funny": "Funny & Chaotic",
        "bossy": "Bossy / Dominant",
        "shy": "Shy & Innocent"
    },

    "body_types": {
        "petite_curvy": "Petite & Curvy",
        "slim_thick": "Slim Thick",
        "hourglass": "Hourglass Figure",
        "fit_curvy": "Fit & Curvy",
        "lean_athletic": "Lean Athletic",
        "voluptuous": "Voluptuous",
        "tall_model": "Tall Model-like",
        "perfect_curvy_blonde": "Perfect Curvy Blonde"
    },

    "body_types_description": {
        "petite_curvy": "short height, compact frame, soft curves, proportionate bust and hips, youthful appearance",
        "slim_thick": "slim waist, fuller hips, rounded curves, toned legs, balanced and modern attractive proportions",
        "hourglass": "defined waist, balanced bust and hips, natural symmetry, classic feminine proportions",
        "fit_curvy": "toned body, visible fitness, soft curves, firm shape, athletic yet feminine look",
        "lean_athletic": "lean muscle tone, light definition, smaller curves, sporty and energetic appearance",
        "voluptuous": "fuller body, soft curves, wider hips, fuller bust, smooth and rounded proportions",
        "tall_model": "tall height, long legs, slim body, elegant posture, fashion model proportions",
        "perfect_curvy_blonde": "hourglass body, full bust, wide hips, defined waist, rounded curves, toned thighs, long blonde hair, soft waves"
    }
}

# Name menu
name_keyboard = create_menu(options, "names", columns=2, prefix="name")

# Age menu
age_keyboard = create_menu(options, "ages", columns=3, prefix="age")

# Character menu
character_keyboard = create_menu(options, "characters", columns=2, prefix="char")

# Body type menu
body_keyboard = create_menu(options, "body_types", columns=2, prefix="body")

body_descriptions = options["body_types_description"]