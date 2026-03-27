import os
import sys
from litellm import completion
from dotenv import load_dotenv

# Load the key from the env file
env_path = os.path.join(os.getcwd(), 'AssertionForge/data/rag_apb/.env')
load_dotenv(env_path)

api_key = os.getenv('GRAPHRAG_API_KEY')
if not api_key:
    # Try reading it directly if load_dotenv fails for some reason
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('GRAPHRAG_API_KEY='):
                    api_key = line.strip().split('=', 1)[1]
                    break
    except Exception:
        pass

if not api_key:
    print(f"Error: GRAPHRAG_API_KEY not found in {env_path}")
    sys.exit(1)

print(f"Loaded API Key: {api_key[:10]}...{api_key[-4:]}")

tested_models = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

success = False
for model in tested_models:
    print(f"\nTesting connectivity with model: {model}")
    try:
        response = completion(
            model=model, 
            messages=[{"role": "user", "content": "This is a test. Reply with 'OK'."}],
            api_key=api_key
        )
        print(f"SUCCESS: Connected to {model}")
        if response and response.choices:
             print(f"Response: {response.choices[0].message.content}")
        success = True
        break
    except Exception as e:
        print(f"FAILURE: Could not connect to {model}")
        error_msg = str(e).split('\n')[0]
        print(f"Error: {error_msg}")

if not success:
    print("\nAll model tests failed. Please check your API key and permissions.")
    sys.exit(1)
