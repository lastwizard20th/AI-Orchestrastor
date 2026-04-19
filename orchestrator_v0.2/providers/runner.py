import requests
from core.db import db
from providers.gemini import ask as gemini_ask
from providers.ollama import ask as ollama_ask


def get_model(model_id:int):
 with db() as c:
  row=c.execute('''SELECT m.*,p.kind,p.base_url,p.api_key,p.name provider_name
                   FROM models m JOIN providers p ON p.id=m.provider_id
                   WHERE m.id=?''',(model_id,)).fetchone()
 return dict(row) if row else None


def run_model(model_id:int, prompt:str):
 m=get_model(model_id)
 if not m:
  raise Exception('Model not found')
 kind=m['kind'].lower()
 if kind=='ollama':
  return ollama_ask(prompt)
 if kind=='gemini':
  return gemini_ask(prompt)
 if kind=='openai':
  return call_openai(m, prompt)
 raise Exception(f'Unsupported provider: {kind}')

def call_openai(m,prompt):
 url=(m['base_url'] or 'https://api.openai.com/v1/chat/completions').rstrip('/')
 headers={'Authorization':f"Bearer {m['api_key']}", 'Content-Type':'application/json'}
 body={
  'model':m['name'],
  'messages':[{'role':'system','content':m['system_prompt']},{'role':'user','content':prompt}],
  'temperature':m['temperature'],
  'max_tokens':m['max_tokens']
 }
 r=requests.post(url, json=body, headers=headers, timeout=120)
 r.raise_for_status()
 data=r.json()
 return data['choices'][0]['message']['content']