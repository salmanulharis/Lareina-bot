import json


def create_menu(options: dict, key: str, columns: int = 2, prefix: str = ""):
    """
    options: full options dict
    key: which menu to generate ("names", "ages", etc.)
    columns: buttons per row
    prefix: optional callback prefix (e.g. "name", "age")
    """

    data = options.get(key, {})
    items = list(data.items())

    keyboard = []
    row = []

    for i, (k, v) in enumerate(items, start=1):

        # handle int values (like age)
        label = str(v)

        row.append({
            "text": label,
            "callback_data": f"{prefix}_{k}" if prefix else k
        })

        if i % columns == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return json.dumps({
        "inline_keyboard": keyboard
    })