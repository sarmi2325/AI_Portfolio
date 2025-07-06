from sentence_transformers import SentenceTransformer
import numpy as np

# Load your model (must match the one used for embeddings)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load chunks and embeddings
with open("vector_store/chunks.txt", "r", encoding="utf-8") as f:
    chunks = f.read().splitlines()
embeddings = np.load("vector_store/embeddings.npy").astype(np.float16)

def cosine_similarity(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(b, a)

def retrieve(query, top_k=4):
    # Get embedding for the query
    query_vec = model.encode([query])[0]
    # Compute cosine similarities
    sims = cosine_similarity(query_vec, embeddings)
    # Get indices of top_k most similar chunks
    top_indices = np.argsort(sims)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]




