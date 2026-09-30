import json

import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = "data/processed/chunks.jsonl"
INDEX_PATH = "data/processed/faiss.index"
QUESTIONS_PATH = "eval/questions.csv"
RESULTS_PATH = "eval/results.csv"
RETRIEVE_K = 10
MIN_SCORE = 0.40

chunks = [json.loads(line) for line in open(CHUNKS_PATH, encoding="utf-8")]
index = faiss.read_index(INDEX_PATH)
model = SentenceTransformer("all-MiniLM-L6-v2")
df = pd.read_csv(QUESTIONS_PATH).fillna("NONE")

rows = []
for _, r in df.iterrows():
    v = model.encode([r["question"]], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(v, RETRIEVE_K)
    sources = [chunks[i]["source"] for i in ids[0]]
    top_score = float(scores[0][0])

    if r["expected_source"] == "NONE":
        rows.append({
            "question": r["question"], "type": "out_of_scope", "expected": "NONE",
            "top_source": sources[0], "top_score": round(top_score, 3),
            "rank": None, "correct": top_score < MIN_SCORE,
        })
    else:
        rank = next((i + 1 for i, s in enumerate(sources) if s == r["expected_source"]), None)
        rows.append({
            "question": r["question"], "type": "in_scope", "expected": r["expected_source"],
            "top_source": sources[0], "top_score": round(top_score, 3),
            "rank": rank, "correct": rank == 1,
        })

res = pd.DataFrame(rows)
res.to_csv(RESULTS_PATH, index=False)

ins = res[res["type"] == "in_scope"]
out = res[res["type"] == "out_of_scope"]


def hit_at(k):
    return float(((ins["rank"].notna()) & (ins["rank"] <= k)).mean())


mrr = float(ins["rank"].apply(lambda x: 1 / x if pd.notna(x) else 0).mean())

print(f"In-scope questions:   {len(ins)}")
print(f"Hit@1: {hit_at(1):.2%}   Hit@3: {hit_at(3):.2%}   Hit@5: {hit_at(5):.2%}   MRR: {mrr:.3f}")
print(f"Out-of-scope questions: {len(out)}")
print(f"Correctly refused (top score < {MIN_SCORE}): {out['correct'].mean():.2%}")

print("\nIn-scope misses (expected source not ranked first):")
print(ins[~ins["correct"]][["question", "expected", "top_source", "rank"]].to_string(index=False))

print("\nOut-of-scope top scores:")
print(out[["question", "top_source", "top_score", "correct"]].to_string(index=False))

print("\nLowest in-scope top scores (risk of wrongly refusing):")
print(ins.sort_values("top_score")[["question", "top_score"]].head(8).to_string(index=False))

print("\nThreshold sweep:")
sweep = []
for t in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
    sweep.append({
        "threshold": t,
        "in_scope_answered": f"{(ins['top_score'] >= t).mean():.1%}",
        "out_of_scope_refused": f"{(out['top_score'] < t).mean():.1%}",
    })
print(pd.DataFrame(sweep).to_string(index=False))