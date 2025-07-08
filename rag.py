
from rank_bm25 import BM25Okapi
import numpy as np

# Load chunked resume
with open("vector_store/chunks.txt", "r", encoding="utf-8") as f:
    chunks = f.read().splitlines()

# Tokenize all chunks (whitespace split works for English)
tokenized_chunks = [chunk.split() for chunk in chunks]

# Initialize BM25
bm25 = BM25Okapi(tokenized_chunks)

def retrieve(query, top_k=5):
    """
    Retrieve top_k relevant resume chunks using BM25 keyword matching.
    """
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]









