import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

def get_embeddings():
    # Use a Windows-compatible cache directory for HuggingFace models
    cache_dir = os.path.join(os.getcwd(), "model_cache")
    os.makedirs(cache_dir, exist_ok=True)

    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        cache_folder=cache_dir
    )
