from services.tasks import list_tasks, save_result
from providers.ollama import ask as ask_ollama
from providers.gemini import ask as ask_gemini

AGENTS={
 'coder':'local',
 'planner':'cloud',
 'plc':'cloud',
 'matlab':'local',
 'auto':'local'
}

def assign_agent(task):
    t=task['title'].lower()
    if 'code' in t or 'python' in t: return 'coder'
    if 'plan' in t or 'roadmap' in t: return 'planner'
    if 'plc' in t: return 'plc'
    if 'matlab' in t: return 'matlab'
    return 'auto'


def run_task(task):
    agent = task['agent'] if task['agent']!='auto' else assign_agent(task)
    provider = AGENTS.get(agent,'local')
    prompt = f"Complete this task and return concise result:\nTask: {task['title']}\nNotes:{task['notes']}"
    result = ask_gemini(prompt) if provider=='cloud' else ask_ollama(prompt)
    save_result(task['id'], result)
    return {'task_id':task['id'],'agent':agent,'provider':provider,'result':result}

def run_pending():
    tasks=[t for t in list_tasks() if t['status']=='todo']
    out=[]
    for t in tasks:
        try: out.append(run_task(t))
        except Exception as e: out.append({'task_id':t['id'],'error':str(e)})
    return out