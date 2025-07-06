import psutil, os

def log_memory(stage=""):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    print(f"[MEMORY] {stage}: {mem:.2f} MB")

# After model load
model = SentenceTransformer("all-MiniLM-L6-v2")
log_memory("After model load")

# After loading embeddings
embeddings = np.load("vector_store/embeddings.npy").astype(np.float16)
log_memory("After loading embeddings")

# After first inference
query_vec = model.encode(["test query"])[0]
log_memory("After first inference")
