import os
from google import genai
KEY=os.getenv('GEMINI_API_KEY','')
MODEL=os.getenv('GEMINI_MODEL','gemini-2.0-flash')
client=genai.Client(api_key=KEY) if KEY else None

def ask(prompt):
    if not client: return 'Gemini key missing'
    r=client.models.generate_content(model=MODEL, contents=prompt)
    return r.text or ''