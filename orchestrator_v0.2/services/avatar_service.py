# ============================================================
# FILE: services/avatar_service.py
# Main AI Avatar State
# ============================================================
import time

STATE = {
    "mood": "idle",       # idle / thinking / speaking / happy
    "speaker": "main",
    "text": "",
    "updated": time.time()
}

def set_avatar(mood="idle", text="", speaker="main"):
    STATE["mood"] = mood
    STATE["speaker"] = speaker
    STATE["text"] = text[:120]
    STATE["updated"] = time.time()

def get_avatar():
    return STATE