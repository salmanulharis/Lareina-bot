import os
import re
from dotenv import load_dotenv
import random
import requests
import time
import uuid
from pathlib import Path
from helpers.setup_helpers import get_json_data

load_dotenv()
COMFYUI_URL = os.getenv("COMFYUI_URL")
COMFYUI_MODEL_NAME = os.getenv("COMFYUI_MODEL_NAME")
LORA_MODEL_KOREAN_NAME = os.getenv("LORA_MODEL_KOREAN_NAME")


# CHARACTER_BASE = (
#     "1girl, solo, ultra realistic, photorealistic, RAW photo, "
#     "soft natural skin, detailed face, real human texture, "
#     "natural lighting, cinematic light, 50mm lens, shallow depth of field, "
#     "beautiful eyes, natural lips, soft expression, "
#     "realistic imperfections, skin pores, subtle makeup"
# )

CHARACTER_BASE = (
    "RAW photo, ultra realistic, photorealistic, 8k, DSLR, "
    "natural skin texture, visible pores, soft imperfections, "
    "cinematic lighting, soft shadows, realistic highlights, "
    "50mm lens, shallow depth of field, bokeh, "
    "natural expression, relaxed face, subtle emotion, "
    "real human proportions, candid moment"
)

USE_IPADAPTER = True
REFERENCE_IMAGE = "aria_reference.png"

# 🔥 Toggle LoRA safely
USE_LORA = False   # ⚠️ SET TRUE only if LoRA nodes exist in ComfyUI


def should_generate_image(text):
    print(f"Checking text: {text}")

    if not text:
        return False

    text = text.lower().strip()

    # 🔹 Direct trigger phrases
    triggers = [
        "send photo", "send image", "send pic", "send picture",
        "selfie", "your photo", "your pic", "your picture",
        "show yourself", "show me you", "i want to see you"
    ]

    # 🔹 Flexible regex patterns
    patterns = [
        r"send.*(photo|image|pic|picture)",
        r"show.*(yourself|you|photo|image|pic)",
        r"can i see.*(you|your face|your pic|your image)",
        r"give me.*(photo|image|pic|picture)",
        r"(generate|create|make).*(image|photo|picture|pic)",
        r"(draw|render).*(image|photo|picture)",
    ]

    # 🔹 Quick keyword + intent logic
    keywords = ["image", "photo", "picture", "pic", "selfie"]
    intents = ["send", "show", "generate", "create", "make", "see"]

    # Check direct triggers
    if any(t in text for t in triggers):
        return True

    # Check regex patterns
    for pattern in patterns:
        if re.search(pattern, text):
            return True

    # Check keyword + intent combo
    if any(k in text for k in keywords) and any(i in text for i in intents):
        return True

    return False


def generate_image_prompt(text, ask_ollama, memory_context):
    prompt = f"""
Convert chat into a realistic selfie scene.

Keep it short (max 15 words).

Context:
{memory_context}

User message:
{text}

Output ONLY scene description.
"""
    try:
        return ask_ollama(prompt)
    except:
        return text

def detect_frame_type(text):
    text = text.lower()

    if any(k in text for k in ["full", "full body", "head to toe", "stand"]):
        return "full"
    elif any(k in text for k in ["selfie", "face", "close"]):
        return "close"
    else:
        return "medium"
    
def build_workflow(prompt):
    json_data = get_json_data()
    seed = json_data.get("character_seed", random.randint(1, 999999999))

    frame = detect_frame_type(prompt)

    if frame == "full":
        width, height = 832, 1216
    elif frame == "close":
        width, height = 512, 768
    else:
        width, height = 640, 896

    workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": COMFYUI_MODEL_NAME}
        },

        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": height, "width": width}
        },

        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": prompt + ", high quality, realistic photo"
            }
        },

        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": (
                    "low quality, blurry, bad anatomy, distorted face, extra limbs, duplicate, watermark, text, ",
                    "cropped, half body, upper body only, close-up, zoomed in, "
                    "cut off legs, missing feet, bad framing, portrait crop"
                )
            }
        },

        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 4.5,
                "denoise": 0.65,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "seed": seed,
                "steps": 30
            }
        },

        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
        },

        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "bot", "images": ["8", 0]}
        }
    }

    # 🔥 SAFE LoRA (only if enabled)
    if USE_LORA:
        workflow["20"] = {
            "class_type": "LoRALoader",
            "inputs": {
                "lora_name": LORA_MODEL_KOREAN_NAME,
                "strength_model": 0.7,
                "strength_clip": 0.5,
                "model": ["4", 0],
                "clip": ["4", 1]
            }
        }

        workflow["3"]["inputs"]["model"] = ["20", 0]
        workflow["6"]["inputs"]["clip"] = ["20", 1]
        workflow["7"]["inputs"]["clip"] = ["20", 1]

    # 🔥 IP Adapter
    if USE_IPADAPTER and Path(REFERENCE_IMAGE).exists():
        workflow["3"]["inputs"]["model"] = ["10", 0]

        workflow["10"] = {
            "class_type": "IPAdapterApply",
            "inputs": {
                "ipadapter": ["12", 0],
                "clip_vision": ["13", 0],
                "image": ["11", 0],
                "model": ["4", 0],
                "weight": 0.75
            }
        }

        workflow["11"] = {
            "class_type": "LoadImage",
            "inputs": {"image": REFERENCE_IMAGE}
        }

        workflow["12"] = {
            "class_type": "IPAdapterModelLoader",
            "inputs": {"ipadapter_file": "ip-adapter_sd15.bin"}
        }

        workflow["13"] = {
            "class_type": "CLIPVisionLoader",
            "inputs": {"clip_name": "clip_vision_g.safetensors"}
        }

    return workflow


def generate_image_comfyui(prompt: str):
    try:
        workflow = build_workflow(prompt)
        client_id = str(uuid.uuid4())

        res = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id}
        )

        print("RAW RESPONSE:", res.text)

        data = res.json()

        if "prompt_id" not in data:
            print("❌ No prompt_id → workflow failed")
            return None

        prompt_id = data["prompt_id"]

        for _ in range(60):
            time.sleep(2)
            history = requests.get(f"{COMFYUI_URL}/history/{prompt_id}").json()

            if prompt_id in history:
                outputs = history[prompt_id]["outputs"]

                for node in outputs.values():
                    if "images" in node:
                        img = node["images"][0]

                        img_res = requests.get(
                            f"{COMFYUI_URL}/view",
                            params={
                                "filename": img["filename"],
                                "subfolder": img["subfolder"],
                                "type": img["type"]
                            }
                        )
                        return img_res.content

        return None

    except Exception as e:
        print("ComfyUI error:", e)
        return None