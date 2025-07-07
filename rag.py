from rank_bm25 import BM25Okapi
import numpy as np

# Load chunks
with open("vector_store/chunk.txt", "r", encoding="utf-8") as f:
    chunks = f.read().splitlines()

# Tokenize each chunk (simple whitespace split works for most English text)
tokenized_chunks = [chunk.split() for chunk in chunks]

# Initialize BM25
bm25 = BM25Okapi(tokenized_chunks)

def retrieve(query, top_k=4):
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = np.argsort(scores)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]







