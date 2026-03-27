# helpers/setup_helpers.py

import json_helper as jhelper

def reset_json_data():
    jhelper.set_all({})
    jhelper.clear_memory()

def get_json_data():
    return jhelper.get_all()

def update_json_data(key, value):
    return jhelper.update_option(key, value)

def set_state(state):
    return jhelper.update_option('state', state)

def get_state():
    return jhelper.get_option('state')
