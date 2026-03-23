import requests
import time
import uuid
from pathlib import Path

COMFYUI_URL = "https://unto-martial-palace-lock.trycloudflare.com"

FIXED_SEED = 42069
MODEL_NAME = "realisticVisionV60B1_v51HyperVAE.safetensors"

CHARACTER_BASE = "1girl, realistic, detailed, consistent character"

USE_IPADAPTER = True
REFERENCE_IMAGE = "aria_reference.png"


def should_generate_image(text):
    keywords = [
        "image", "photo", "picture", "selfie",
        "show", "look like", "wearing", "send me"
    ]
    return any(k in text.lower() for k in keywords)


def generate_image_prompt(text, ask_ollama):
    prompt = f"""
You generate image prompts.
Reply ONLY with a short scene description (max 15 words).

User: {text}
"""
    try:
        return ask_ollama(prompt)
    except:
        return text


def build_workflow(prompt):
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 7,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler",
                "scheduler": "normal",
                "seed": FIXED_SEED,
                "steps": 15
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": MODEL_NAME}
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 384, "width": 384}
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": prompt + ", high quality, detailed, realistic"
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["4", 1],
                "text": "blurry, ugly, bad quality"
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

    # 🔥 IP-Adapter
    if USE_IPADAPTER and Path(REFERENCE_IMAGE).exists():
        workflow["3"]["inputs"]["model"] = ["10", 0]

        workflow["10"] = {
            "class_type": "IPAdapterApply",
            "inputs": {
                "ipadapter": ["12", 0],
                "clip_vision": ["13", 0],
                "image": ["11", 0],
                "model": ["4", 0],
                "weight": 0.8
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

        prompt_id = res.json()["prompt_id"]

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