import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'AssertionForge/src'))
print(sys.path)

try:
    import utils_LLM
    print("Imported utils_LLM successfully")
    print(dir(utils_LLM))
    from utils_LLM import llm_inference
    print("Imported llm_inference successfully")
except Exception as e:
    print(f"Error: {e}")
