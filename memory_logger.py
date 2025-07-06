import psutil
import os

def log_memory(stage=""):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    print(f"[MEMORY] {stage}: {mem:.2f} MB")

