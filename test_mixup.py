import sys
import os
import shutil

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from backend.services.github_loader import clone_repository
from backend.services.chunker import load_repository_files, chunk_documents
from backend.services.embeddings import get_embeddings
from backend.services.vector_store import create_vector_store
from backend.services.rag_pipeline import generate_repo_summary

def test_repo(url):
    print(f"Testing {url}...")
    repo_path = clone_repository(url)
    print(f"Cloned to {repo_path}")
    docs = load_repository_files(repo_path)
    chunks = chunk_documents(docs)
    print(f"Total chunks: {len(chunks)}")
    if len(chunks) > 90:
        chunks = chunks[:90]
    embeddings = get_embeddings()
    vectordb = create_vector_store(chunks, embeddings)
    summary = generate_repo_summary(vectordb)
    print(summary[:500])
    print("="*50)
    shutil.rmtree(repo_path, ignore_errors=True)

test_repo("https://github.com/torvalds/linux")
test_repo("https://github.com/facebook/react")
