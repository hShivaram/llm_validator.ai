# model_to_validate/summarizer/app.py

import logging
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import numpy as np

# Initialize embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")
# Dummy in-memory vector store
VECTOR_STORE = np.random.rand(100, 384)  
DOCS = [f"Document snippet {i}" for i in range(100)]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("summarizer")

def embed_text(text: str) -> np.ndarray:
    """Return embedding for a given text."""
    if not text or not isinstance(text, str):
        raise ValueError("Input to embed_text must be a non-empty string")
    vec = embedder.encode([text])[0]
    logger.debug(f"Embedded text shape: {vec.shape}")
    return vec

def retrieve_similar(query_vec: np.ndarray, top_k: int = 5):
    """Retrieve top_k most similar doc snippets."""
    knn = NearestNeighbors(n_neighbors=top_k, metric="cosine").fit(VECTOR_STORE)
    distances, indices = knn.kneighbors([query_vec])
    results = [(DOCS[idx], float(dist)) for idx, dist in zip(indices[0], distances[0])]
    logger.info(f"Retrieved top {top_k} docs for query")
    return results

def build_summary_prompt(context_docs, question):
    """
    Build a prompt to ask an LLM for a concise summary.
    """
    docs_text = "\n".join(f"- {doc}" for doc, _ in context_docs)
    prompt = (
        f\"\"\"\nYou are a smart assistant.\n"
        f"Synthesize the following documents into a 3-sentence summary answering:\n"
        f"\"{question}\"\n\n"
        f"Context:\n{docs_text}\n\"\"\""
    )
    return prompt

def generate_summary(question: str):
    """Full RAG-style summary generation."""
    q_vec = embed_text(question)
    top_docs = retrieve_similar(q_vec, top_k=3)
    prompt = build_summary_prompt(top_docs, question)
    # Simulate API call to an LLM (placeholder)
    logger.info("Sending prompt to LLM for generation")
    return f"[LLM SUMMARY for '{question}']\n" + " ".join(doc for doc, _ in top_docs)

# Example usage
if __name__ == "__main__":
    q = "What are the main challenges in AI governance?"
    print(generate_summary(q))
