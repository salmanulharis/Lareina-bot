# services/image_service.py — Image generation pipeline.
# Detects image requests, builds ComfyUI workflow, polls for result, sends photo.

import re
import uuid
import time
import random
import requests
from pathlib import Path

from config.settings import (
    COMFYUI_URL,
    COMFYUI_MODEL_NAME,
    LORA_MODEL_NAME,
    USE_LORA,
    USE_IPADAPTER,
    REFERENCE_IMAGE,
)
from prompts.image_prompt import build_image_prompt
from utils.llm import ask_llm
from utils.telegram import send_message, send_photo


# ── Trigger detection ─────────────────────────────────────────────────────────

_TRIGGER_PHRASES = [
    "send photo", "send image", "send pic", "send picture",
    "selfie", "your photo", "your pic", "your picture",
    "show yourself", "show me you", "i want to see you",
]

_TRIGGER_PATTERNS = [
    r"send.*(photo|image|pic|picture)",
    r"show.*(yourself|you|photo|image|pic)",
    r"can i see.*(you|your face|your pic|your image)",
    r"give me.*(photo|image|pic|picture)",
    r"(generate|create|make).*(image|photo|picture|pic)",
]


def should_request_image(text: str) -> bool:
    if not text:
        return False
    lower = text.lower().strip()

    if any(phrase in lower for phrase in _TRIGGER_PHRASES):
        return True

    for pattern in _TRIGGER_PATTERNS:
        if re.search(pattern, lower):
            return True

    keywords = ["image", "photo", "picture", "pic", "selfie"]
    intents = ["send", "show", "generate", "create", "make", "see"]
    if any(k in lower for k in keywords) and any(i in lower for i in intents):
        return True

    return False


# ── Frame detection ───────────────────────────────────────────────────────────

def _detect_frame_type(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in ["full", "full body", "head to toe", "stand"]):
        return "full"
    if any(k in lower for k in ["selfie", "face", "close"]):
        return "close"
    return "medium"


_FRAME_DIMENSIONS = {
    "full":   (832, 1216),
    "close":  (512, 768),
    "medium": (640, 896),
}

_FRAME_FRAMING_TEXT = {
    "full": (
        "full body, head to toe visible, feet visible, standing pose, "
        "entire body in frame, long shot, camera far, full height"
    ),
    "close": "close-up selfie, face focus, upper body",
    "medium": "medium shot, upper body, waist up",
}


# ── Main entry point ──────────────────────────────────────────────────────────

def handle_image_request(chat_id: int, user_text: str, session: dict, memory_summary: str):
    """Generate and send one image. Fails silently — no retry loops."""

    reaction = random.choice([
        "wait… *fixes hair* lemme take one 😌📸",
        "*smiles softly* okay okay… one sec 💕",
        "*adjusts camera* don't laugh 😝",
        "*leans closer* this one's just for you 📸",
    ])
    send_message(chat_id, reaction)

    try:
        final_prompt = build_image_prompt(
            user_text=user_text,
            session=session,
            memory_summary=memory_summary,
            ask_llm_fn=ask_llm,
        )
        print(f"[IMAGE] Final prompt: {final_prompt}")

        image_bytes = _run_comfyui(final_prompt, session, user_text)

        if image_bytes:
            send_photo(chat_id, image_bytes)
        else:
            print(f"[IMAGE] ComfyUI returned no image for chat_id={chat_id}")
            # No fallback message — don't spam the user

    except Exception as e:
        print(f"[IMAGE] Pipeline error for chat_id={chat_id}: {e}")


# ── ComfyUI workflow ──────────────────────────────────────────────────────────

def _run_comfyui(prompt: str, session: dict, user_text: str) -> bytes | None:
    """Submit workflow to ComfyUI, poll until image is ready, return raw bytes."""
    if not COMFYUI_URL:
        print("[IMAGE] COMFYUI_URL not set — skipping generation")
        return None

    try:
        workflow = _build_workflow(prompt, session, user_text)
        client_id = str(uuid.uuid4())

        res = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=10,
        )
        res.raise_for_status()
        data = res.json()

        prompt_id = data.get("prompt_id")
        if not prompt_id:
            print(f"[IMAGE] ComfyUI rejected workflow: {data}")
            return None

        # Poll history until done (max 60 attempts × 2s = 2 minutes)
        for attempt in range(60):
            time.sleep(2)
            history_res = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            history = history_res.json()

            if prompt_id not in history:
                continue

            outputs = history[prompt_id].get("outputs", {})
            for node_output in outputs.values():
                if "images" not in node_output:
                    continue
                img_meta = node_output["images"][0]
                img_res = requests.get(
                    f"{COMFYUI_URL}/view",
                    params={
                        "filename": img_meta["filename"],
                        "subfolder": img_meta.get("subfolder", ""),
                        "type": img_meta.get("type", "output"),
                    },
                    timeout=15,
                )
                print(f"[IMAGE] Retrieved after {attempt + 1} attempts")
                return img_res.content

        print("[IMAGE] Timed out waiting for ComfyUI")
        return None

    except Exception as e:
        print(f"[IMAGE] ComfyUI request error: {e}")
        return None


def _build_workflow(prompt: str, session: dict, user_text: str) -> dict:
    seed = session.get("character_seed", random.randint(1, 999_999_999))
    frame = _detect_frame_type(user_text)
    width, height = _FRAME_DIMENSIONS[frame]

    negative = (
        "low quality, blurry, bad anatomy, distorted face, extra limbs, "
        "duplicate, watermark, text, cropped, half body, cut off legs, "
        "missing feet, bad framing, portrait crop, nsfw"
    )

    workflow = {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": COMFYUI_MODEL_NAME},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": height, "width": width},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": prompt + ", high quality, realistic photo"},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": negative},
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
                "steps": 30,
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "bot", "images": ["8", 0]},
        },
    }

    if USE_LORA and LORA_MODEL_NAME:
        workflow["20"] = {
            "class_type": "LoRALoader",
            "inputs": {
                "lora_name": LORA_MODEL_NAME,
                "strength_model": 0.7,
                "strength_clip": 0.5,
                "model": ["4", 0],
                "clip": ["4", 1],
            },
        }
        workflow["3"]["inputs"]["model"] = ["20", 0]
        workflow["6"]["inputs"]["clip"] = ["20", 1]
        workflow["7"]["inputs"]["clip"] = ["20", 1]

    if USE_IPADAPTER and Path(REFERENCE_IMAGE).exists():
        workflow["10"] = {
            "class_type": "IPAdapterApply",
            "inputs": {
                "ipadapter": ["12", 0],
                "clip_vision": ["13", 0],
                "image": ["11", 0],
                "model": ["4", 0],
                "weight": 0.75,
            },
        }
        workflow["11"] = {
            "class_type": "LoadImage",
            "inputs": {"image": REFERENCE_IMAGE},
        }
        workflow["12"] = {
            "class_type": "IPAdapterModelLoader",
            "inputs": {"ipadapter_file": "ip-adapter_sd15.bin"},
        }
        workflow["13"] = {
            "class_type": "CLIPVisionLoader",
            "inputs": {"clip_name": "clip_vision_g.safetensors"},
        }
        workflow["3"]["inputs"]["model"] = ["10", 0]

    return workflow