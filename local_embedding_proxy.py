import time
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
import argparse

app = Flask(__name__)

# Load the model globally
print("Loading sentence-transformer model: all-MiniLM-L6-v2 ...")
# You can change the model if you want, this one is small and fast
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully.")

@app.route('/v1/embeddings', methods=['POST'])
def embeddings():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "Missing input field"}), 400
    
    inputs = data['input']
    if isinstance(inputs, str):
        inputs = [inputs]
        
    # Generate embeddings
    embeddings = EMBEDDING_MODEL.encode(inputs).tolist()
    
    # Format response like OpenAI
    data_response = []
    for i, emb in enumerate(embeddings):
        data_response.append({
            "object": "embedding",
            "index": i,
            "embedding": emb
        })
        
    return jsonify({
        "object": "list",
        "data": data_response,
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "usage": {
            "prompt_tokens": 0,
            "total_tokens": 0
        }
    })

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
