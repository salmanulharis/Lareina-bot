import json
import os

_FILE = "data.json"


# ---------- Internal ----------
def _read():
    if not os.path.exists(_FILE):
        return {}

    try:
        with open(_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def _write(data: dict):
    with open(_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ---------- Core API ----------

# ✅ Get all options
def get_all():
    return _read()


# ✅ Get single option
def get_option(key, default=None):
    data = _read()
    return data.get(key, default)


# ✅ Update option (add if not exists)
def update_option(key, value):
    data = _read()
    data[key] = value   # add or update
    _write(data)
    return value


# ✅ Delete option
def delete_option(key):
    data = _read()

    if key in data:
        del data[key]
        _write(data)
        return True

    return False


# ---------- Extra (Bulk) ----------

# ✅ Set full dict (overwrite)
def set_all(data: dict):
    _write(data)
    return data


# ✅ Update multiple options
def update_options(new_data: dict):
    data = _read()
    data.update(new_data)
    _write(data)
    return data


# ✅ Delete multiple keys
def delete_options(keys: list):
    data = _read()

    for k in keys:
        data.pop(k, None)

    _write(data)
    return data


# ✅ Clear all
def clear_all():
    _write({})
    return {}