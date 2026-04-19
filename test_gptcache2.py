from gptcache.adapter.adapter import adapt
import gptcache.adapter.api as api
from gptcache import cache
from gptcache.embedding import Huggingface
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

embedder = Huggingface(model="sentence-transformers/all-MiniLM-L6-v2")
data_manager = get_data_manager(
    cache_base=CacheBase("sqlite", sql_url="sqlite:///mycache.db"),
    vector_base=VectorBase("faiss", dimension=embedder.dimension, index_path="mycache.index")
)
cache.init(
    embedding_func=embedder.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(max_distance=0.1)
)

query_msgs = [{"role": "user", "content": "hello world"}]

# Simulate litellm returned object
class Msg:
    content = "my LLM reply string"
class Ch:
    message = Msg()
class Resp:
    choices = [Ch()]

import threading

# Test put
api.put(resp=Resp(), messages=query_msgs)

# Test get
cached = api.get(messages=query_msgs)
print("api.get returned:", type(cached), cached)

