import random
from services.voice_phrase import build_voice_text
from services.audio_manager import synth_to_base64

VOICES = ["af_sarah", "af_bella", "af_nicole"]

engine = None
try:
    from kokoro_tts import Kokoro
    engine = Kokoro()
except:
    engine = None


def make_voice_reply(user_text="", intent="general", provider="local"):
    if engine is None:
        return {"text": "", "audio_b64": None}

    phrase = build_voice_text(user_text, intent, provider)
    voice = random.choice(VOICES)

    try:
        b64 = synth_to_base64(engine, phrase, voice)
    except:
        b64 = None

    return {
        "text": phrase,
        "audio_b64": b64
    }