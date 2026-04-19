import os
import json
import requests

FILE = "data/providers.json"
os.makedirs("data", exist_ok=True)


DEFAULT_PROVIDERS = {
    "local-ollama": {
        "name": "local-ollama",
        "type": "ollama",
        "url": "http://localhost:11434/api/generate",
        "api_key": "",
        "model": "qwen3.5:9b",
        "enabled": True
    },
    "gemini-main": {
        "name": "gemini-main",
        "type": "gemini",
        "url": "",
        "api_key": "",
        "model": "gemini-2.0-flash",
        "enabled": True
    }
}


def load_all():
    if not os.path.exists(FILE):
        save_all(DEFAULT_PROVIDERS)

    with open(FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_all(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_provider(name):
    data = load_all()
    return data.get(name)


def save_provider(obj):
    data = load_all()
    data[obj["name"]] = obj
    save_all(data)


def delete_provider(name):
    data = load_all()
    if name in data:
        del data[name]
        save_all(data)


def test_provider(name):
    p = get_provider(name)
    if not p:
        return {"ok": False, "error": "Provider not found"}

    typ = p.get("type")

    try:
        if typ == "ollama":
            r = requests.post(
                p["url"],
                json={
                    "model": p["model"],
                    "prompt": "Say hello",
                    "stream": False
                },
                timeout=15
            )
            r.raise_for_status()
            return {"ok": True, "message": "Ollama connected"}

        elif typ == "gemini":
            if not p.get("api_key"):
                return {"ok": False, "error": "Missing API key"}
            return {"ok": True, "message": "Gemini key detected"}

        elif typ == "openai":
            if not p.get("api_key"):
                return {"ok": False, "error": "Missing API key"}
            return {"ok": True, "message": "OpenAI key detected"}

        return {"ok": True, "message": "Basic config valid"}

    except Exception as e:
        return {"ok": False, "error": str(e)}