# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma

# pyrefly: ignore [missing-import]
from langchain_core.documents import Document
import uuid
import os


def create_vector_store(
    chunks,
    embeddings
):

    docs = []

    for chunk in chunks:

        docs.append(
            Document(
                page_content=chunk["content"],
                metadata={
                    "source": chunk["file"]
                }
            )
        )

    # Use in-memory Chroma to avoid database corruption issues
    db = Chroma.from_documents(
        docs,
        embeddings,
        collection_name="repo_analysis"
    )

    return db
