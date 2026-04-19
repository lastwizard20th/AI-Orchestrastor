# ============================================================
# FILE: services/speech_bus.py
# Main AI Voice Queue + Sequential Speech Control
# ============================================================
import threading
import queue
import time
import uuid
from pathlib import Path

VOICE_DIR = Path("static/voice")
VOICE_DIR.mkdir(parents=True, exist_ok=True)

_jobs = queue.Queue()
_busy = False
_lock = threading.Lock()

engine = None
try:
    from kokoro_tts import Kokoro
    engine = Kokoro()
except:
    engine = None


class SpeechJob:
    def __init__(self, text, voice="af_sarah", speaker="main"):
        self.id = uuid.uuid4().hex
        self.text = text
        self.voice = voice
        self.speaker = speaker
        self.url = None
        self.status = "queue"


def _synthesize(job):
    if engine is None:
        return None

    filename = f"{job.id}.mp3"
    out = VOICE_DIR / filename

    # try api 1
    try:
        engine.synthesize(
            text=job.text,
            voice=job.voice,
            output_path=str(out)
        )
        return f"/static/voice/{filename}"
    except:
        pass

    # try api 2
    try:
        engine.generate(
            text=job.text,
            voice=job.voice,
            file=str(out)
        )
        return f"/static/voice/{filename}"
    except:
        pass

    return None


def worker():
    global _busy
    while True:
        job = _jobs.get()
        with _lock:
            _busy = True

        try:
            job.status = "running"
            job.url = _synthesize(job)
            job.status = "done"
            EVENT_LOG.append({
                "type": "speech_done",
                "speaker": job.speaker,
                "text": job.text,
                "url": job.url,
                "ts": time.time()
            })
        except Exception as e:
            EVENT_LOG.append({
                "type": "speech_error",
                "speaker": job.speaker,
                "error": str(e),
                "ts": time.time()
            })
        finally:
            with _lock:
                _busy = False
            _jobs.task_done()


EVENT_LOG = []
threading.Thread(target=worker, daemon=True).start()


def speak(text, voice="af_sarah", speaker="main"):
    if not text.strip():
        return None
    job = SpeechJob(text=text[:240], voice=voice, speaker=speaker)
    _jobs.put(job)
    EVENT_LOG.append({
        "type": "speech_queue",
        "speaker": speaker,
        "text": text,
        "ts": time.time()
    })
    return job.id


def is_busy():
    with _lock:
        return _busy


def get_events(after=0):
    return [x for x in EVENT_LOG if x["ts"] > after]