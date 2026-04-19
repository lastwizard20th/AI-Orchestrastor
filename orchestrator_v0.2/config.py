import os
OLLAMA_URL = os.getenv('OLLAMA_URL','http://localhost:11434/api/generate')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL','qwen3.5:9b')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY','')
GEMINI_MODEL = os.getenv('GEMINI_MODEL','gemini-2.0-flash')
CHROMA_PATH = 'data'
EMBED_MODEL = 'all-MiniLM-L6-v2'