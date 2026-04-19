import requests, os
URL=os.getenv('OLLAMA_URL','http://localhost:11434/api/generate')
MODEL=os.getenv('OLLAMA_MODEL','qwen3.5:9b')

def ask(prompt):
    r=requests.post(URL,json={'model':MODEL,'prompt':prompt,'stream':False},timeout=180)
    r.raise_for_status()
    return r.json().get('response','')