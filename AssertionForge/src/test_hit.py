import sys
import os
sys.path.append(os.path.abspath('Project/AssertionForge/src'))
import utils_LLM

prompt = "Hello, this is a test prompt. Generate a plan."
print("First call:")
utils_LLM.llm_inference(utils_LLM.get_llm(), prompt, "test")
print("\nSecond call:")
utils_LLM.llm_inference(utils_LLM.get_llm(), prompt, "test")

