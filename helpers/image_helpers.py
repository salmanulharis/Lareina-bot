import random
import requests
import time
import uuid
from pathlib import Path
from helpers.setup_helpers import get_json_data

COMFYUI_URL = "https://hypothetical-mitsubishi-genes-tracy.trycloudflare.com"

MODEL_NAME = "realisticVision.safetensors"

CHARACTER_BASE = (
    "1girl, solo, ultra realistic, photorealistic, RAW photo, "
    "soft natural skin, detailed face, real human texture, "
    "natural lighting, cinematic light, 50mm lens, shallow depth of field, "
    "beautiful eyes, natural lips, soft expression, "
    "realistic imperfections, skin pores, subtle makeup"
)

USE_IPADAPTER = True
REFERENCE_IMAGE = "aria_reference.png"

# 🔥 Toggle LoRA safely
USE_LORA = False   # ⚠️ SET TRUE only if LoRA nodes exist in ComfyUI


def should_generate_image(text):
    if not text:
        return False

    text = text.lower()

    triggers = [
        "send photo",
        "send image",
        "selfie",
        "show yourself",
        "show me you",
        "i want to see you"
    ]

    return any(t in text for t in triggers)


def generate_image_prompt(text, ask_ollama):
    prompt = f"""
You generate image prompts.
Reply ONLY with a realistic photo scenario.
Focus on natural human situations, lighting, and emotion.
Max 20 words.

User: {text}
"""
    try:
        return ask_ollama(prompt)
    except:
        return text


def build_workflow(prompt):
    json_data = get_json_data()
    seed = json_data.get("character_seed", random.randint(1, 999999999))

    workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": MODEL_NAME}
        },

        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 768, "width": 512}
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
                    "cartoon, anime, cgi, render, painting, fake, doll, plastic skin, "
                    "over smooth, blurry, low quality, bad anatomy, deformed face, "
                    "extra fingers, mutated hands, unrealistic, oversharpen, overexposed"
                )
            }
        },

        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 5.5,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": seed,
                "steps": 28
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
                "lora_name": "korean_beauty.safetensors",
                "strength_model": 0.6,
                "strength_clip": 0.6,
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
                "weight": 0.6
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