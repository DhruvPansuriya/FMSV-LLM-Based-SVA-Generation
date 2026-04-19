# Add your own LLM client

import os
import time
import re
from litellm import completion
from dotenv import load_dotenv

from gptcache.adapter.adapter import adapt
import gptcache.adapter.api as api
from gptcache import cache
from gptcache.embedding import Huggingface
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

_gptcache_initialized = False

def init_gptcache():
    global _gptcache_initialized
    if _gptcache_initialized:
        return
    print("Initiating GPTCache with Semantic Search capabilities...")
    embedder = Huggingface(model="sentence-transformers/all-MiniLM-L6-v2")
    cache_path = os.path.join(os.getcwd(), 'AssertionForge', 'gptcache_data')
    os.makedirs(cache_path, exist_ok=True)
    sqlite_path = os.path.join(cache_path, 'gptcache.db')
    faiss_path = os.path.join(cache_path, 'faiss.index')

    data_manager = get_data_manager(
        cache_base=CacheBase("sqlite", sql_url=f"sqlite:///{sqlite_path}"),
        vector_base=VectorBase("faiss", dimension=embedder.dimension, index_path=faiss_path)
    )

    cache.init(
        embedding_func=embedder.to_embeddings,
        data_manager=data_manager,
        similarity_evaluation=SearchDistanceEvaluation(max_distance=0.08),
    )
    _gptcache_initialized = True

init_gptcache()

# Load key from env
def load_keys():
    # Try to locate .env
    # Current working directory is project root
    possible_paths = [
        os.path.join(os.getcwd(), 'AssertionForge/data/rag_apb/.env'),
        os.path.join(os.path.dirname(__file__), '../data/rag_apb/.env'),
        os.path.join(os.path.dirname(__file__), '../../data/rag_apb/.env'), # In case cwd is src
    ]
    path_found = None
    for p in possible_paths:
        if os.path.exists(p):
            load_dotenv(p)
            print(f"Loaded .env from {p}")
            break
            
    # LiteLLM needs OPENAI_API_KEY
    if 'GRAPHRAG_API_KEY' in os.environ and 'OPENAI_API_KEY' not in os.environ:
        os.environ['OPENAI_API_KEY'] = os.environ['GRAPHRAG_API_KEY']

load_keys()

class LiteLLMAgent:
    def __init__(self, model):
        self.model = model
    
    def invoke(self, prompt, temperature=0.7):
        messages = [{"role": "user", "content": prompt}]
        max_retries = 10 
        base_delay = 5 
         
        for attempt in range(max_retries):  
            try: 
                start_time = time.time()
                # Using litellm defaults for OpenAI models, or groq/ prefix if needed
                resp = adapt(
                    completion,
                    cache_data_convert=api._cache_data_converter,
                    update_cache_callback=api._update_cache_callback,
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    num_retries=0 # Disable internal retries so we control the backoff
                )
                
                elapsed = time.time() - start_time
                
                if elapsed < 0.5:
                    print(f"⚡ [GPTCache Hit] Bypassed Groq API locally! (Took {elapsed:.3f}s)")
                else:
                    print(f"Step complete. Pausing 15s to respect Groq API rate limits... (Took {elapsed:.3f}s)")
                    time.sleep(15) 
                
                return resp.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                if "RateLimitError" in error_str or "429" in error_str:
                    # Extract wait time if available, otherwise exponential backoff
                    wait_time = base_delay * (2 ** attempt)
                    
                    # Try to parse 'Please try again in XmYs' or 'Xs'
                    # e.g. "Please try again in 7m19.776s" or "Please try again in 12.5s"
                    match = re.search(r"try again in (?:(\d+)m)?(\d+(\.\d+)?)s", error_str)
                    if match:
                        mins = float(match.group(1)) if match.group(1) else 0
                        secs = float(match.group(2))
                        wait_time = mins * 60 + secs + 1.0 # Add buffer
                    
                    print(f"Rate limit hit. Waiting {wait_time:.2f}s before retry {attempt+1}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"Error invoking LLM {self.model}: {e}")
                    raise e
        
        raise Exception(f"Max retries exceeded for LLM {self.model}")

def count_prompt_tokens(prompt):
    # Rough estimation
    return len(prompt.split())

def get_llm(model_name="gpt-4o", **kwargs):
    # model_name comes from config FLAGS.llm_model 
    return LiteLLMAgent(model_name)

def llm_inference(agent, prompt, identifier="", temperature=0.7):
    # Matches gen_plan.py signature: llm_inference(llm_agent, full_prompt, f"ID")
    print(f"LLM Inference for {identifier}...")
    try:
        return agent.invoke(prompt, temperature=temperature)
    except Exception as e:
        print(f"LLM Inference Failed detail: {e}")
        return ""
