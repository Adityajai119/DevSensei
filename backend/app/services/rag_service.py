import os
# Disable ChromaDB telemetry warnings
os.environ["CHROMA_TELEMETRY_ENABLED"] = "FALSE"

from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path="./vector_db")
collection = chroma_client.get_or_create_collection("repo_chunks")

# Use a small, fast embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def index_repo_files(repo_name: str, files: List[Dict[str, Any]]):
    """Index all code/text files from a repo into ChromaDB."""
    for file in files:
        if file.get("type") == "file" and file.get("content") and file.get("language") in [
            "python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "php", "ruby", "markdown", "json", "yaml", "html", "css"
        ]:
            text = file["content"]
            file_chunks = chunk_text(text)
            metadatas = [{
                "repo": repo_name,
                "file": file["name"],
                "path": file["path"]
            }] * len(file_chunks)
            ids = [f"{repo_name}_{file['name']}_chunk_{i}" for i in range(len(file_chunks))]
            embeddings = embedder.encode(file_chunks).tolist()
            collection.add(
                documents=file_chunks,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )

def query_repo_context(repo_name: str, question: str, top_k: int = 5) -> List[str]:
    """Query ChromaDB for relevant code chunks as context for a question."""
    question_embedding = embedder.encode([question])[0].tolist()
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where={"repo": repo_name}
    )
    return results["documents"][0] if results["documents"] else []

# Main RAG function for answering repo questions
def answer_repo_question(repo_name: str, files: List[Dict[str, Any]], question: str) -> str:
    # Index files if not already indexed (idempotent for demo)
    index_repo_files(repo_name, files)
    # Query for relevant context
    context_chunks = query_repo_context(repo_name, question)
    # Return context to be used with Gemini
    return "\n---\n".join(context_chunks) if context_chunks else "No relevant context found." 