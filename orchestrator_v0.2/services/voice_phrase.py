import random
import re

PHRASES = [
    "Let me check {topic}.",
    "I'm working on {topic}.",
    "Give me a moment with {topic}.",
    "I understand your request about {topic}.",
    "Looking into {topic} now.",
    "Preparing details about {topic}.",
    "I'll help you with {topic}.",
    "Analyzing {topic}.",
    "Optimizing {topic} for you.",
    "Reviewing {topic}.",
    "Working through {topic}.",
    "Gathering information about {topic}.",
    "Let me think about {topic}.",
    "I'm processing {topic}.",
    "Building a solution for {topic}.",
    "Checking the best option for {topic}.",
    "I'll handle {topic}.",
    "Taking care of {topic} now.",
    "Let's solve {topic}.",
    "Generating results for {topic}.",
    "I’m on it: {topic}.",
    "Starting with {topic}.",
]

DONE_PHRASES = [
    "Done.",
    "I've finished that.",
    "Task completed.",
    "Everything is ready.",
    "That part is complete."
]


def extract_topic(text: str) -> str:
    words = re.findall(r"[A-Za-z0-9_]+", text)
    if not words:
        return "this task"
    return " ".join(words[:5])


def build_voice_text(user_msg: str, intent="general", provider="local") -> str:
    topic = extract_topic(user_msg)

    if intent == "empty":
        return "I'm ready."

    phrase = random.choice(PHRASES)
    return phrase.format(topic=topic)