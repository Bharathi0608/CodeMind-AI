# CodeMind-AI 🧠🚀

CodeMind-AI is an intelligent, interactive web-based repository analyzer and conversational agent. It allows users to clone any public GitHub repository, analyze its structure and codebase, generate interactive Mermaid architecture diagrams, and engage in context-aware Q&A about the codebase.

---

## ✨ Features

- **GitHub Repository Cloning & Parsing**: Automatically clones a repository, filters source files, and processes code documents.
- **RAG-Powered Code Q&A**: Uses Retrieval-Augmented Generation (RAG) to answer technical questions about your code using LangChain, Google GenAI, or Groq (Llama models).
- **Interactive Architecture Flowcharts**: Generates structural execution diagrams using Mermaid, rendered interactively with panning, zooming, and nodes color-coded by tier (backend vs. helper services).
- **Comprehensive Reports**: Automatically produces markdown reports covering architecture overview, tools/frameworks detected, and step-by-step functionality, ready for download.
- **Clean Responsive Web UI**: Premium design built with modern CSS (glassmorphism, vibrant dark mode gradients) and vanilla JavaScript.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Main web framework for the API endpoints and serving static files.
- **Uvicorn**: ASGI web server implementation.
- **LangChain & LangChain-Community**: Orchestrates the document parsing, vector stores, and LLM chains.
- **ChromaDB**: High-performance, lightweight vector database for semantic code search.
- **APIs & LLMs**: Supports **Groq Cloud (Llama 3.3)** and **Google Gemini** models.

### Frontend
- **HTML5 & Vanilla CSS**: Premium dark-themed user interface with sleek glassmorphism styling and custom animations.
- **Vanilla JavaScript**: Handle user events, asynchronous API calls, markdown parsing (`marked.js`), and dynamic diagram interaction (`svg-pan-zoom`).
- **Mermaid.js**: Dynamically renders architectural charts.

---

## 📂 Project Structure

```text
CodeMind-AI/
│
├── backend/                    # FastAPI Backend Application
│   ├── services/               # Core business logic / pipelines
│   │   ├── chunker.py          # Document loader & text splitter
│   │   ├── embeddings.py       # Embeddings generator
│   │   ├── github_loader.py    # Repository cloner
│   │   ├── rag_pipeline.py     # RAG model & summary execution
│   │   └── vector_store.py     # Chroma vector database creator
│   ├── app.py                  # Main API server & routes
│   └── config.py               # Application configuration
│
├── frontend/                   # Client-side Static Assets
│   ├── index.html              # Main user interface
│   ├── script.js               # Event handlers & visual renders
│   └── style.css               # Modern dark-mode stylesheet
│
├── requirements.txt            # Python dependencies
└── .env                        # Local environment secrets
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Bharathi0608/CodeMind-AI.git
cd CodeMind-AI
```

### 3. Setup Virtual Environment
* **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **On macOS/Linux:**
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables Configuration
Create a `.env` file in the root of the project:
```env
GROQ_API_KEY=your_groq_api_key_here
# Optional: GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🚀 How to Run

Start the FastAPI application by running:
```bash
python -m backend.app
```

The application will start, serving both the API and the frontend user interface. Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🔒 License

Distributed under the MIT License. See `LICENSE` for more information.