# keyboards/builder.py — Generic inline keyboard builder.
# Takes a dict of {key: label} and returns a JSON-encoded Telegram InlineKeyboardMarkup.

import json


def build_inline_keyboard(
    items: dict,
    columns: int = 2,
    callback_prefix: str = "",
) -> str:
    """
    items: { "callback_key": "Button Label", ... }
    columns: how many buttons per row
    callback_prefix: prepended to each callback_data with underscore separator

    Returns JSON string suitable for Telegram reply_markup.
    """
    keyboard = []
    row = []

    for i, (key, label) in enumerate(items.items(), start=1):
        callback_data = f"{callback_prefix}_{key}" if callback_prefix else key
        row.append({"text": str(label), "callback_data": callback_data})

        if i % columns == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return json.dumps({"inline_keyboard": keyboard})