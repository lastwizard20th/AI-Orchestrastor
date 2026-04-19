import json, re


from providers.gemini import ask as ask_gemini
from providers.ollama import ask as ask_ollama
from services.tasks import add_task


def extract_json(text:str):
    m = re.search(r'\[.*\]', text, re.S)
    return m.group(0) if m else '[]'


def plan_goal(goal:str):
    prompt = f'''
Break this goal into actionable tasks.
Return ONLY JSON array.
Format:
[
  {{"title":"task1","priority":"high","notes":"..."}},
  {{"title":"task2","priority":"medium","notes":"..."}}
]
Goal: {goal}
'''
    try:
        raw = ask_gemini(prompt)
    except:
        raw = ask_ollama(prompt)
    try:
        data = json.loads(extract_json(raw))
    except Exception:
        data = []

    for item in data:
        add_task(
            title=item.get('title','Untitled Task'),
            priority=item.get('priority','medium'),
            notes=item.get('notes','')
        )
    return data