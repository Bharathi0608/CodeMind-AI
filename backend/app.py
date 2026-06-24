import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import re
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from backend.services.github_loader import clone_repository
from backend.services.chunker import load_repository_files, chunk_documents
from backend.services.embeddings import get_embeddings
from backend.services.vector_store import create_vector_store
from backend.services.rag_pipeline import ask_question, generate_repo_summary

app = FastAPI(title="CodeMind AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
GLOBAL_STATE = {
    "vectordb": None,
    "repo_path": None
}

class AnalyzeRequest(BaseModel):
    repo_url: str
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.2
    chunk_size: int = 1000
    chunk_overlap: int = 200

class ChatRequest(BaseModel):
    query: str
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.2

@app.post("/api/analyze")
async def analyze_repo(req: AnalyzeRequest):
    try:
        shutil.rmtree("./chroma_db", ignore_errors=True)
        
        repo_path = clone_repository(req.repo_url)
        GLOBAL_STATE["repo_path"] = repo_path
        
        docs = load_repository_files(repo_path)
        chunks = chunk_documents(docs, chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
        
        embeddings = get_embeddings()
        vectordb = create_vector_store(chunks, embeddings)
        GLOBAL_STATE["vectordb"] = vectordb
        
        summary = generate_repo_summary(vectordb, model_name=req.model_name, temperature=req.temperature)
        
        # Extract Mermaid code
        mermaid_code = None
        clean_summary = summary
        
        mermaid_match = re.search(r'```mermaid(.*?)```', summary, re.DOTALL | re.IGNORECASE)
        if mermaid_match:
            mermaid_code = mermaid_match.group(1).strip()
            clean_summary = re.sub(r'## 📊 Architecture Flowchart\s*```mermaid.*?```', '', clean_summary, flags=re.DOTALL | re.IGNORECASE)
            clean_summary = re.sub(r'```mermaid.*?```', '', clean_summary, flags=re.DOTALL | re.IGNORECASE)
        else:
            blocks = re.findall(r'```(.*?)```', summary, re.DOTALL)
            for block in blocks:
                if "graph " in block.lower() or "flowchart " in block.lower() or "graph\n" in block.lower() or "flowchart\n" in block.lower():
                    if '\n' in block:
                        first_line, rest = block.split('\n', 1)
                        if "graph" in first_line.lower() or "flowchart" in first_line.lower():
                            mermaid_code = block.strip()
                        else:
                            mermaid_code = rest.strip()
                    else:
                        mermaid_code = block.strip()
                    break

        if mermaid_code:
            mermaid_code = re.sub(r'\|>\s*', '| ', mermaid_code)
            mermaid_code = re.sub(r'(?<=\]|\)|\}|\w)\s+(\b\w+)\s*(-->|-.->|==>)', r'\n\1 \2', mermaid_code)
            stripped_code = mermaid_code.strip()
            if not (stripped_code.startswith("flowchart") or stripped_code.startswith("graph") or stripped_code.startswith("sequenceDiagram")):
                mermaid_code = "flowchart TD\n" + mermaid_code
            
            clean_lines = []
            for line in mermaid_code.split('\n'):
                stripped = line.strip()
                if stripped.startswith('classDef') or stripped.startswith('style') or stripped.startswith('class '):
                    continue
                
                placeholders = []
                def hide_label(match):
                    placeholders.append(match.group(0))
                    return f"__LABEL_{len(placeholders)-1}__"
                
                temp_line = re.sub(r'\|([^|]+)\|', hide_label, line)
                
                def repl_shape(match):
                    preceding, node_id, shape_start, label, shape_end = match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)
                    clean_label = label.replace('"', '').replace("'", "")
                    return f'{preceding}{node_id}{shape_start}"{clean_label}"{shape_end}'
                
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\[\[)\s*(.*?)\s*(\]\])', repl_shape, temp_line)
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\(\[)\s*(.*?)\s*(\]\))', repl_shape, temp_line)
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\[\()\s*(.*?)\s*(\)\])', repl_shape, temp_line)
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\(\()\s*(.*?)\s*(\)\))', repl_shape, temp_line)
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\[)\s*(.*?)\s*(\])', repl_shape, temp_line)
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\()\s*(.*?)\s*(\))', repl_shape, temp_line)
                temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\{)\s*(.*?)\s*(\})', repl_shape, temp_line)
                
                for idx, placeholder in enumerate(placeholders):
                    temp_line = temp_line.replace(f"__LABEL_{idx}__", placeholder)
                    
                clean_lines.append(temp_line)
            mermaid_code = '\n'.join(clean_lines)

        return {
            "success": True,
            "summary": clean_summary,
            "mermaid_code": mermaid_code
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not GLOBAL_STATE["vectordb"]:
        raise HTTPException(status_code=400, detail="Please analyze a repository first.")
    
    try:
        response = ask_question(
            GLOBAL_STATE["vectordb"],
            req.query,
            model_name=req.model_name,
            temperature=req.temperature
        )
        return {"success": True, "answer": response}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Serve frontend static files
frontend_path = os.path.join(project_root, "frontend")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if not full_path or full_path == "":
        full_path = "index.html"
    file_path = os.path.join(frontend_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
