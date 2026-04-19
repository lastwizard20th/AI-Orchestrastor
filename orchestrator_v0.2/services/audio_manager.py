import io
import base64
import subprocess
import tempfile
from pathlib import Path


def synth_to_base64(engine, text, voice):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wf:
        wav_path = wf.name

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mf:
        mp3_path = mf.name

    try:
        engine.synthesize(
            text=text,
            voice=voice,
            output_path=wav_path
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", wav_path,
            "-vn",
            "-ar", "24000",
            "-ac", "1",
            "-b:a", "64k",
            mp3_path
        ]

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(mp3_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        return b64

    finally:
        try:
            Path(wav_path).unlink(missing_ok=True)
            Path(mp3_path).unlink(missing_ok=True)
        except:
            pass