from flask import Flask, request

from handlers.message_handler import handle_message, handle_callback

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    print('Incoming: ', data)
    print_values(data)

    if "message" in data or "hi" in data:
        handle_message(data["message"])

    elif "callback_query" in data:
        handle_callback(data["callback_query"])

    return {"status": "ok"}


def print_values(d):
    for key, value in d.items():
        if isinstance(value, dict):
            print_values(value)
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    app.run(port=5000, debug=True)