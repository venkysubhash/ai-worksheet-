import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=400):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

def build_index(text):
    chunks = chunk_text(text)
    embeddings = model.encode(chunks)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings).astype("float32"))

    return index, chunks

def search_index(index, chunks, question, k=4):
    q_embedding = model.encode([question])

    distances, ids = index.search(
        np.array(q_embedding).astype("float32"),
        k
    )

    results = []

    for idx in ids[0]:
        if idx < len(chunks):
            results.append(chunks[idx])

    return "\n".join(results)