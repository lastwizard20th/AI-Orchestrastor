import os, json

SETTINGS_FILE = 'data/settings.json'
os.makedirs('data', exist_ok=True)

DEFAULT = {
    "system_prompt": "You are a helpful AI assistant.",
    "provider": "auto",
    "temperature": 0.4,
    "allow_tools": True,
    "allow_cloud": True,

    "main_provider": "local",

    "team_members": [
        {"name": "Main AI", "provider": "local", "role": "leader"},
        {"name": "Gemini", "provider": "gemini", "role": "advisor"},
        {"name": "Coder", "provider": "local", "role": "coder"},
        {"name": "Planner", "provider": "gemini", "role": "planner"}
    ]
}


def load_all():
    if not os.path.exists(SETTINGS_FILE):
        save_all({'default': DEFAULT})
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_all(data):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_profile(name='default'):
    data = load_all()
    return data.get(name, DEFAULT)

def save_profile(name, cfg):
    data = load_all()
    data[name] = cfg
    save_all(data)


def delete_profile(name):
    data = load_all()
    if name in data and name != 'default':
        del data[name]
        save_all(data)