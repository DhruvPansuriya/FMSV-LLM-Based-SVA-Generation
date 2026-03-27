import os
import requests
from dotenv import load_dotenv

load_dotenv("AssertionForge/data/rag_apb/.env")

groq_key = os.getenv("GROQ_API_KEY")
openai_key = os.getenv("GRAPHRAG_API_KEY")

print(f"Testing Groq API... Key len: {len(groq_key) if groq_key else 0}")
try:
    headers = {"Authorization": f"Bearer {groq_key}"}
    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
    print(f"Groq Response: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
except Exception as e:
    print(f"Groq Error: {e}")

print(f"Testing OpenAI API... Key len: {len(openai_key) if openai_key else 0}")
try:
    headers = {"Authorization": f"Bearer {openai_key}"}
    # Test embeddings endpoint
    data = {
        "input": "test",
        "model": "text-embedding-3-small"
    }
    response = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=data, timeout=10)
    print(f"OpenAI Response: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
except Exception as e:
    print(f"OpenAI Error: {e}")
