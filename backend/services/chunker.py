# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os

SUPPORTED_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".md"
)

IGNORE_FOLDERS = {
    ".git",
    "venv",
    "__pycache__",
    "node_modules"
}

def load_repository_files(repo_path):

    documents = []

    for root, dirs, files in os.walk(repo_path):

        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_FOLDERS
        ]

        for file in files:

            if file.endswith(
                SUPPORTED_EXTENSIONS
            ):

                file_path = os.path.join(
                    root,
                    file
                )

                try:

                    with open(
                        file_path,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        content = f.read()

                    documents.append(
                        {
                            "file": file_path,
                            "content": content
                        }
                    )

                except Exception:
                    pass

    return documents

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = []

    for doc in documents:       

        text_chunks = splitter.split_text(
            doc["content"]
        )

        for chunk in text_chunks:

            chunks.append({
                "file": doc["file"],
                "content": chunk
            })

    return chunks       
