from providers.ollama import ask as local
from providers.gemini import ask as cloud

def teamwork_run(task):
    plan=cloud('Break into steps: '+task)
    code=local('Implement best solution for: '+task)
    review=cloud('Review this output:\n'+code)
    return f'PLAN:\n{plan}\n\nCODE:\n{code}\n\nREVIEW:\n{review}'