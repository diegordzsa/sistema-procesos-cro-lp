import json
import os

STATE_FILE = "data/state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"last_check": None, "tasks": {}, "alerted": []}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


