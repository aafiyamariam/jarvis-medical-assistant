import json
import re
from pathlib import Path

import pymupdf

RAW = Path("data/raw")
OUT = Path("data/processed/chunks.jsonl")
CHUNK_WORDS = 180
OVERLAP = 30

# Everything after the first of these markers is link lists, references or footer
CUT_MARKERS = [
    "Start Here",
    "The information on this site should not be used",
    "Review Date",
    "References",
]


def extract_text(pdf_path):
    doc = pymupdf.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def clean(text):
    """Return (page_url, cleaned_body_text)."""
    text = re.sub(r"-\n(\w)", r"\1", text)  # rejoin hyphenated line breaks
    text = re.sub(r"\s+", " ", text)

    # browser print header/footer lines
    text = re.sub(r"\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2} [AP]M .*?https://\S+# \d+/\d+", " ", text)
    text = re.sub(
        r"An official website of the United States government Here.s how you know "
        r"National Institutes of Health / National Library of Medicine",
        " ",
        text,
    )

    # grab the page URL and drop everything before it (breadcrumbs etc.)
    url = ""
    m = re.search(r"URL of this page:\s*(\S+)", text)
    if m:
        url = m.group(1)
        if url.startswith("//"):
            url = "https:" + url
        text = text[m.end():]

    # cut off link lists, references and footer
    cut_points = [text.find(k) for k in CUT_MARKERS if text.find(k) != -1]
    if cut_points:
        text = text[:min(cut_points)]

    # remove bracketed links like [https://medlineplus.gov/iron.html]
    text = re.sub(r"\[https?://[^\]]*\]", "", text)
    text = re.sub(r"\s+([.,;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return url, text.strip()


def chunk_words(text, size, overlap):
    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        piece = words[start:start + size]
        if len(piece) < 30 and start > 0:
            break
        chunks.append(" ".join(piece))
    return chunks


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for pdf in sorted(RAW.glob("*.pdf")):
            url, text = clean(extract_text(pdf))
            chunks = chunk_words(text, CHUNK_WORDS, OVERLAP)
            for i, c in enumerate(chunks):
                record = {"source": pdf.stem, "url": url, "chunk_id": i, "text": c}
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"{pdf.name}: {len(text.split())} words -> {len(chunks)} chunks | {url}")
            total += len(chunks)
    print(f"Total chunks: {total}")


if __name__ == "__main__":
    main()