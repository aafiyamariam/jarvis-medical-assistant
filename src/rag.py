import json
import logging
import os
import re
import time

import faiss
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from sentence_transformers import SentenceTransformer

logging.getLogger("google_genai").setLevel(logging.ERROR)
load_dotenv()

CHUNKS_PATH = "data/processed/chunks.jsonl"
INDEX_PATH = "data/processed/faiss.index"
MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest"]
TOP_K = 5
MIN_SCORE = 0.40  # below this, treat the question as not covered by the documents

EMERGENCY_TERMS = [
    "chest pain", "can't breathe", "cannot breathe", "heart attack right now",
    "having a stroke", "overdose", "unconscious", "severe bleeding",
]
CRISIS_TERMS = ["suicide", "kill myself", "want to die", "end my life", "self-harm", "hurt myself"]

EMERGENCY_MSG = (
    "This may be a medical emergency. Please call your local emergency number "
    "or go to the nearest emergency room right away. I can only share general "
    "information and can't help in an emergency."
)
CRISIS_MSG = (
    "I'm really sorry you're feeling this way. You deserve support from a real person. "
    "Please contact a local crisis line or emergency service right now, or reach out "
    "to someone you trust and tell them how you feel."
)

SYSTEM_PROMPT = """You are Jarvis, a medical information assistant.
Rules:
- Answer ONLY using the numbered context passages below.
- Cite the passages you use like [1] or [2].
- First decide whether the passages directly answer the question that was asked.
- If they do not answer it, reply only: "I don't have enough information in my documents to answer that."
- If they answer only part of it, give that part, then say clearly that the documents do not fully cover the question and suggest asking a doctor or pharmacist.
- Never diagnose, never recommend a specific medicine dose, never replace a doctor.
- Do not introduce yourself or add a greeting. Start directly with the answer.
- Keep the answer clear and under 150 words.
- End with: "This is general information, not medical advice." """

chunks = [json.loads(line) for line in open(CHUNKS_PATH, encoding="utf-8")]
index = faiss.read_index(INDEX_PATH)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def retrieve(question, k=TOP_K):
    v = embedder.encode([question], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(v, k)
    return [(chunks[i], float(s)) for i, s in zip(ids[0], scores[0])]


def call_llm(prompt):
    for model in MODELS:
        for attempt in range(3):
            try:
                resp = client.models.generate_content(model=model, contents=prompt)
                return resp.text
            except errors.ServerError:
                time.sleep(4 * (attempt + 1))
    return "The language model is busy right now. Please try again in a few minutes."


def answer(question):
    q = question.lower()
    if any(t in q for t in CRISIS_TERMS):
        return CRISIS_MSG, []
    if any(t in q for t in EMERGENCY_TERMS):
        return EMERGENCY_MSG, []

    hits = [(c, s) for c, s in retrieve(question) if s >= MIN_SCORE]
    if not hits:
        return "I don't have enough information in my documents to answer that.", []

    context = "\n\n".join(
        f"[{i + 1}] ({c['source']}) {c['text']}" for i, (c, _) in enumerate(hits)
    )
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}"
    return call_llm(prompt), hits


def cited_sources(text, hits):
    """Return unique (source, url) pairs for the passages the answer actually cited."""
    nums = {
        int(n)
        for group in re.findall(r"\[([\d,\s]+)\]", text)
        for n in re.findall(r"\d+", group)
    }
    seen, out = set(), []
    for n in sorted(nums):
        if 1 <= n <= len(hits):
            c = hits[n - 1][0]
            if c["url"] not in seen:
                seen.add(c["url"])
                out.append((c["source"], c["url"]))
    return out


if __name__ == "__main__":
    while True:
        question = input("\nAsk Jarvis (or type quit): ").strip()
        if question.lower() in ("quit", "exit", ""):
            break
        text, hits = answer(question)
        print("\n" + text)
        sources = cited_sources(text, hits)
        if sources:
            print("\nSources:")
            for name, url in sources:
                print(f"  - {name}: {url}")