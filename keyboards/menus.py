import json


def food_menu():

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🍕 Pizza", "callback_data": "pizza"},
                {"text": "🍔 Burger", "callback_data": "burger"}
            ]
        ]
    }

    return json.dumps(keyboard)


def drink_menu():

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🥤 Coke", "callback_data": "coke"},
                {"text": "🥤 Pepsi", "callback_data": "pepsi"}
            ]
        ]
    }

    return json.dumps(keyboard)