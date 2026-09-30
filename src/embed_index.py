import json
import faiss
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = "data/processed/chunks.jsonl"
INDEX_PATH = "data/processed/faiss.index"

with open(CHUNKS_PATH, encoding="utf-8") as f:
    chunks = [json.loads(line) for line in f]

model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [c["text"] for c in chunks]
emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=True).astype("float32")

index = faiss.IndexFlatIP(emb.shape[1])
index.add(emb)
faiss.write_index(index, INDEX_PATH)
print(f"Indexed {index.ntotal} chunks")