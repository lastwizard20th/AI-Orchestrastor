# services/orchestrator.py

from services.history_service import add_history, get_recent
from services.memory_service import search_memory, save_memory_async
from services.settings import get_profile

from services.team_engine import run_team_chat, run_private_with_support

from services.avatar_service import set_avatar
from services.voice_service import make_voice_reply


# ==========================================
# INTENT
# ==========================================
def classify(msg: str):
    m = msg.lower()

    if any(x in m for x in ["team", "multi agent", "group chat"]):
        return "teamwork"

    if any(x in m for x in ["plan", "roadmap", "schedule"]):
        return "planner"

    if any(x in m for x in ["code", "python", "bug", "script"]):
        return "coder"

    return "general"


# ==========================================
# CONTEXT
# ==========================================
def build_message_with_context(message, session_id):
    recent = get_recent(session_id)
    mem = search_memory(message)

    return f"""
Conversation History:
{recent}

Relevant Memory:
{mem}

User Request:
{message}
""".strip()


# ==========================================
# SHORT VOICE TEXT
# ==========================================
def build_short_voice(reply: str):
    if not reply:
        return "Okay."

    text = reply.strip().replace("\n", " ")

    if len(text) > 140:
        text = text[:140].rsplit(" ", 1)[0]

    return text


# ==========================================
# MAIN CHAT
# ==========================================
def handle_chat(
    message,
    session_id="default",
    mode="auto",
    profile="default",
    room_type="private"
):
    cfg = get_profile(profile)
    intent = classify(message)

    full_prompt = build_message_with_context(message, session_id)

    # --------------------------------------
    # USER STARTED
    # --------------------------------------
    set_avatar("thinking", message, "main")

    # ======================================
    # TEAM MODE
    # ======================================
    if room_type == "team":

        team_messages = run_team_chat(full_prompt, cfg)

        final_text = "\n\n".join(
            f"{x['sender']}: {x['text']}"
            for x in team_messages
        )

        provider = "team-engine"

        add_history(session_id, "user", message)
        add_history(session_id, "ai", final_text)

        save_memory_async(message)

        short_voice = build_short_voice(final_text)
        voice = make_voice_reply(short_voice, intent, provider)
        

        set_avatar("speaking", short_voice, "main")

        return {
            "intent": intent,
            "provider": provider,
            "response": final_text,
            "team_messages": team_messages,
            "voice_text": voice.get("text", ""),
            "audio_b64": voice.get("audio_b64")
        }

    # ======================================
    # PRIVATE MODE
    # ======================================
    reply, provider = run_private_with_support(full_prompt, cfg)

    add_history(session_id, "user", message)
    add_history(session_id, "ai", reply)

    save_memory_async(message)

    short_voice = build_short_voice(reply)
    voice = make_voice_reply(short_voice, intent, provider)

    set_avatar("speaking", short_voice, "main")

    return {
        "intent": intent,
        "provider": provider,
        "response": reply,
        "voice_text": voice.get("text", ""),
        "audio_b64": voice.get("audio_b64")
    }