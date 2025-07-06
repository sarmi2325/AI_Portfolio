from sklearn.feature_extraction.text import TfidfVectorizer

# Load chunks
with open("vector_store/chunks.txt", "r", encoding="utf-8") as f:
    chunks = f.read().splitlines()

# Create vectorizer and embeddings
vectorizer = TfidfVectorizer()
embeddings = vectorizer.fit_transform(chunks)

def retrieve(query, top_k=4):
    query_vec = vectorizer.transform([query])
    sims = (embeddings * query_vec.T).toarray().flatten()
    top_indices = np.argsort(sims)[-top_k:][::-1]
    return [chunks[i] for i in top_indices]






