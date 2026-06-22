from services.chunker import (
load_repository_files,
chunk_documents
)

repo_path = "repositories/streamlit"

docs = load_repository_files(
repo_path
)

print(
f"Files Loaded: {len(docs)}"
)

chunks = chunk_documents(
docs
)

print(
f"Chunks Created: {len(chunks)}"
)

print("\nFirst Chunk:\n")

print(
chunks[0]["content"][:500]
)
