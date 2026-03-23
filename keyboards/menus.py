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
        "petite": "Petite",
        "slim": "Slim",
        "curvy": "Curvy",
        "athletic": "Athletic",
        "average": "Average",
        "tall_slim": "Tall & Slim",
        "fit_curvy": "Fit & Curvy"
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