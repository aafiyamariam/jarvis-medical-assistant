import json
import faiss
from sentence_transformers import SentenceTransformer

chunks = [json.loads(line) for line in open("data/processed/chunks.jsonl", encoding="utf-8")]
index = faiss.read_index("data/processed/faiss.index")
model = SentenceTransformer("all-MiniLM-L6-v2")

questions = [
    "What are the symptoms of low blood sugar?",
    "How is high blood pressure treated?",
    "What triggers an asthma attack?",
    "What are the warning signs of a stroke?",
    "What foods commonly cause allergies?",
    "Do antibiotics work for a cold?",
]

for q in questions:
    v = model.encode([q], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(v, 3)
    print(f"\nQ: {q}")
    for s, i in zip(scores[0], ids[0]):
        c = chunks[i]
        print(f"  {s:.3f} [{c['source']}] {c['text'][:110]}...")