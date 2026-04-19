import os
from litellm import completion
from gptcache.adapter.adapter import adapt
from gptcache import cache
from gptcache.embedding import Huggingface
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

embedder = Huggingface(model="sentence-transformers/all-MiniLM-L6-v2")
data_manager = get_data_manager(
    cache_base=CacheBase("sqlite", sql_url="sqlite:///mycache2.db"),
    vector_base=VectorBase("faiss", dimension=embedder.dimension, index_path="mycache2.index")
)
cache.init(
    embedding_func=embedder.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(max_distance=0.1)
)

class MockMessage:
    def __init__(self, content): self.content = content
class MockChoice:
    def __init__(self, message): self.message = message
class MockResponse:
    def __init__(self, choices): self.choices = choices

def my_cache_data_converter(cache_data):
    return MockResponse([MockChoice(MockMessage(cache_data))])

def my_update_cache_callback(llm_data, update_cache_func):
    update_cache_func(llm_data.choices[0].message.content)

class Dummy:
    def __init__(self):
        self.choices = [MockChoice(MockMessage("This is a test response"))]
def fake_completion(**kwargs):
    return Dummy()

query_msgs = [{"role": "user", "content": "What is 2+2?"}]

resp1 = adapt(
    fake_completion,
    cache_data_convert=my_cache_data_converter,
    update_cache_callback=my_update_cache_callback,
    messages=query_msgs
)
print("Response 1:", resp1.choices[0].message.content)

resp2 = adapt(
    fake_completion,
    cache_data_convert=my_cache_data_converter,
    update_cache_callback=my_update_cache_callback,
    messages=query_msgs
)
print("Response 2:", resp2.choices[0].message.content)

