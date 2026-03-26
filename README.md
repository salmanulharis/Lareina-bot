## Telegram Flask Bot

A simple Telegram bot built with Flask for handling food and drink orders via interactive menus.

---

### Features
- Handles Telegram webhook events
- Interactive food and drink selection menus
- User session management
- Easy to deploy on any server supporting Python & Flask

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/telegram_flask_bot.git
cd telegram_flask_bot
```

### 2. Create and activate a virtual environment (Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:

```env
# .env example
BOT_TOKEN=your_telegram_bot_token
MODEL_NAME=mistral
LLM_API_URL=http://localhost:11434/api/generate
COMFYUI_URL=http://localhost:8188/api/v1/generate
COMFYUI_MODEL_NAME=realisticVision.safetensors
LORA_MODEL_KOREAN_NAME=korean_beauty.safetensors
```

---

## Running the Bot Locally

```bash
python app.py
```
The bot will start on `http://localhost:5000/webhook`.

---

## Setting the Telegram Webhook

Telegram cannot reach localhost directly. You must expose your local server to the internet (e.g., using [ngrok](https://ngrok.com/)) or deploy to a public server.

Set the webhook with:

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://yourdomain.com/webhook
```
Replace `<TOKEN>` with your bot token and `yourdomain.com` with your public URL.

---

## Project Structure

- `app.py` - Main Flask app
- `handlers/` - Message and callback handlers
- `keyboards/` - Menu keyboard layouts
- `services/` - User session management
- `utils/` - Telegram API utilities
- `config.py` - Loads environment variables

---

## Troubleshooting

- Ensure your bot token is correct in the `.env` file
- If running locally, use ngrok or similar to expose your port
- Check Flask logs for incoming webhook data

---

## Credits

Created by [Your Name].

---

## License

MIT License