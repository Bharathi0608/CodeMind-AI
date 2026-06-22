# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma

# pyrefly: ignore [missing-import]
from langchain_core.documents import Document
import uuid


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

    db = Chroma.from_documents(
        docs,
        embeddings,
        collection_name=f"repo_{uuid.uuid4().hex}"
    )

    return db
