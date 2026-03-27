# app.py — Flask webhook entry point
# Receives all Telegram updates and routes to the appropriate handler.

from flask import Flask, request
from handlers.message_handler import handle_message
from handlers.callback_handler import handle_callback

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if not data:
        return {"status": "no data"}, 400

    print("[WEBHOOK] Incoming:", data)

    if "message" in data:
        handle_message(data["message"])

    elif "callback_query" in data:
        handle_callback(data["callback_query"])

    return {"status": "ok"}


if __name__ == "__main__":
    app.run(port=5000, debug=True)