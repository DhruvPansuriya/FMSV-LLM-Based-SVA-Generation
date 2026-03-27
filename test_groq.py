import os
import sys
from litellm import completion
from dotenv import load_dotenv

# Load the key from the env file
env_path = os.path.join(os.getcwd(), 'AssertionForge/data/rag_apb/.env')
load_dotenv(env_path)

api_key = os.getenv('GROQ_API_KEY')
print(f"Loaded Groq Key: {api_key[:10]}...{api_key[-4:]}")

model = "groq/llama-3.1-8b-instant"

print(f"\nTesting connectivity with model: {model}")
try:
    response = completion(
        model=model, 
        messages=[{"role": "user", "content": "This is a test. Reply with 'OK'."}],
        api_key=api_key
    )
    print(f"SUCCESS: Connected to {model}")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"FAILURE: Could not connect to {model}")
    print(f"Error: {e}")
