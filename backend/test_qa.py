from services.chunker import (
load_repository_files,
chunk_documents
)

from services.embeddings import (
get_embeddings
)

from services.vector_store import (
create_vector_store
)

from services.rag_pipeline import (
ask_question
)

repo_path = "repositories/streamlit"

docs = load_repository_files(
repo_path
)

chunks = chunk_documents(
docs
)

print("Creating Vector DB...")

embeddings = get_embeddings()

vectordb = create_vector_store(
chunks[:500],
embeddings
)

print("Ready!")

question = input(
"\nAsk Question: "
)

answer = ask_question(
vectordb,
question
)

print("\n")
print(answer)
