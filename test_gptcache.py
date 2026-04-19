from gptcache.adapter.adapter import adapt
import gptcache.adapter.api as api
from gptcache import cache
from gptcache.embedding import Huggingface
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

embedder = Huggingface(model="all-MiniLM-L6-v2")
data_manager = get_data_manager(
    cache_base=CacheBase("sqlite", sql_url="sqlite:///mycache.db"),
    vector_base=VectorBase("faiss", dimension=embedder.dimension, index_path="mycache.index")
)
cache.init(
    embedding_func=embedder.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(max_distance=0.1)
)

def my_completion(**kwargs):
    print("CALLED DUMMY COMPLETION!")
    return "Paris is the capital."

query_msgs = [{"role": "user", "content": "What is the capital of France?"}]

resp1 = adapt(
    my_completion,
    cache_data_convert=api._cache_data_converter,
    update_cache_callback=api._update_cache_callback,
    messages=query_msgs
)
print("Response 1:", resp1)

resp2 = adapt(
    my_completion,
    cache_data_convert=api._cache_data_converter,
    update_cache_callback=api._update_cache_callback,
    messages=query_msgs
)
print("Response 2:", resp2)

