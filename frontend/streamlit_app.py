import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# pyrefly: ignore [missing-import]
import streamlit as st

import importlib
import backend.services.github_loader
import backend.services.chunker
import backend.services.embeddings
import backend.services.vector_store
import backend.services.rag_pipeline

# Dynamically reload backend modules to avoid stale pycache / Streamlit caching
importlib.reload(backend.services.github_loader)
importlib.reload(backend.services.chunker)
importlib.reload(backend.services.embeddings)
importlib.reload(backend.services.vector_store)
importlib.reload(backend.services.rag_pipeline)

from backend.services.github_loader import clone_repository
from backend.services.chunker import load_repository_files, chunk_documents
from backend.services.embeddings import get_embeddings
from backend.services.vector_store import create_vector_store
from backend.services.rag_pipeline import ask_question, generate_repo_summary

st.set_page_config(page_title="CodeMind AI", layout="wide", page_icon="🧠")

# Inject Custom Premium CSS
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {display: none !important;}
    header {visibility: hidden;}

    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@500;700&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Top Navigation Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 1.5rem;
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .top-nav-logo {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        color: #fff;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .top-nav-link {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .top-nav-badge {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        color: #fff;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        box-shadow: 0 0 10px rgba(0, 114, 255, 0.3);
    }

    /* Hero Section */
    .hero-container {
        padding: 3rem 2rem;
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95)), url('https://www.transparenttextures.com/patterns/cubes.png');
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        animation: fadeIn 1s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #cbd5e1;
        font-weight: 400;
        opacity: 0.9;
    }

    /* Expander & Cards */
    div[data-testid="stExpander"] {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stExpander"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.05);
    }

    /* Premium Inline Form Styling */
    div[data-testid="stForm"] {
        border: 1px solid rgba(128, 128, 128, 0.2);
        background: rgba(30, 41, 59, 0.03);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-top: 1.5rem;
    }
    div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stForm"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 114, 255, 0.3) !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem 0;
        margin-top: 2rem;
        border-top: 1px solid rgba(128, 128, 128, 0.2);
        color: #64748b;
        font-size: 0.85rem;
        font-family: 'Inter', sans-serif;
    }
    .footer span {
        background: linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Render Top Nav Bar
st.markdown("""
<div class="top-nav">
    <div class="top-nav-logo">🧠 CodeMind AI</div>
    <div style="display: flex; gap: 15px; align-items: center;">
        <span class="top-nav-link">Architect Mode</span>
        <span class="top-nav-badge">V1.0 Stable</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Render Hero Header
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🧠 CodeMind AI</div>
    <div class="hero-subtitle">The Ultimate AI-Powered Codebase Architect & Knowledge Assistant</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if "vectordb" not in st.session_state:
    st.session_state.vectordb = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""
if "repo_path" not in st.session_state:
    st.session_state.repo_path = ""
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📊 Dashboard & Flow"
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# --- Sidebar for setup & configuration ---
with st.sidebar:
    st.header("Setup & Configuration")
    repo_url_input = st.text_input("GitHub Repository URL", value=st.session_state.repo_url)
    
    # Model configuration options
    st.subheader("⚙️ AI Configuration")
    
    # Build list of available models based on keys
    available_models = []
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        available_models.extend(["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
    available_models.extend(["gemini-2.0-flash", "gemini-1.5-pro"])
    
    # Check session state for model
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = available_models[0]
    
    selected_model = st.selectbox(
        "LLM Model", 
        options=available_models, 
        index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
    )
    st.session_state.selected_model = selected_model
    
    # Temperature slider
    if "llm_temperature" not in st.session_state:
        st.session_state.llm_temperature = 0.2
    llm_temperature = st.slider("LLM Temperature", min_value=0.0, max_value=1.0, value=st.session_state.llm_temperature, step=0.1)
    st.session_state.llm_temperature = llm_temperature
    
    # Chunking settings
    st.subheader("✂️ Chunker Settings")
    if "chunk_size" not in st.session_state:
        st.session_state.chunk_size = 1000
    if "chunk_overlap" not in st.session_state:
        st.session_state.chunk_overlap = 200
        
    chunk_size = st.slider("Chunk Size", min_value=500, max_value=3000, value=st.session_state.chunk_size, step=100)
    st.session_state.chunk_size = chunk_size
    
    chunk_overlap = st.slider("Chunk Overlap", min_value=50, max_value=1000, value=st.session_state.chunk_overlap, step=50)
    st.session_state.chunk_overlap = chunk_overlap

    st.divider()
    
    if st.button("Analyze Repository"):
        if repo_url_input:
            # Auto-clean double-pasted / concatenated URLs
            url = repo_url_input.strip()
            if "https://" in url:
                parts = url.split("https://")
                if len(parts) > 2:
                    url = "https://" + parts[-1]
            
            st.session_state.repo_url = url
            
            # Wipe out any legacy vector databases on disk just to be extremely safe
            import shutil
            shutil.rmtree("./chroma_db", ignore_errors=True)
            
            try:
                with st.spinner("Cloning repository..."):
                    repo_path = clone_repository(url)
                    st.session_state.repo_path = repo_path
                    
                with st.spinner("Loading and chunking files..."):
                    docs = load_repository_files(repo_path)
                    chunks = chunk_documents(docs, chunk_size=st.session_state.chunk_size, chunk_overlap=st.session_state.chunk_overlap)
                    
                with st.spinner("Creating Vector Database (Local AI Model, No Rate Limits!)..."):
                    embeddings = get_embeddings()
                    vectordb = create_vector_store(chunks, embeddings)
                    st.session_state.vectordb = vectordb
                    
                with st.spinner("Generating Repository Summary & Mermaid Diagrams..."):
                    summary = generate_repo_summary(vectordb, model_name=st.session_state.selected_model, temperature=st.session_state.llm_temperature)
                    st.session_state.summary = summary
                    
                st.success("Analysis Complete!")
                st.session_state.chat_history = []
            except Exception as e:
                err_msg = str(e)
                if "GitCommandError" in type(e).__name__ or "git.exc.GitCommandError" in type(e).__name__:
                    st.error("⚠️ **Git Clone Error**: Could not clone the repository. Please make sure the URL is correct (not duplicated) and the repository is public.")
                elif "RESOURCE_EXHAUSTED" in err_msg:
                    st.error("⚠️ **Gemini API Rate Limit Exceeded (429)**. You have hit the free tier quota limit. Please wait a moment and try again, or check your API key status.")
                else:
                    st.error(f"⚠️ **Error during analysis**: {err_msg}")
            
        else:
            st.error("Please enter a valid GitHub URL.")

    # Export Session Button
    if st.session_state.summary:
        st.divider()
        st.header("Export")
        
        # Build Export String
        export_content = f"# Repository Analysis: {st.session_state.repo_url}\n\n"
        export_content += f"{st.session_state.summary}\n\n"
        export_content += "---\n\n## Chat Session\n\n"
        for msg in st.session_state.chat_history:
            role = "🗣️ User" if msg["role"] == "user" else "🤖 CodeMind AI"
            export_content += f"**{role}**:\n{msg['content']}\n\n"
            
        st.download_button(
            label="📥 Download Session Report",
            data=export_content,
            file_name="codemind_session_report.md",
            mime="text/markdown"
        )

# pyrefly: ignore [missing-import]
import streamlit.components.v1 as components
import re

def render_mermaid(mermaid_code):
    safe_mermaid_code = mermaid_code.replace('`', '\\`').replace('$', '\\$')
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/svg-pan-zoom@3.6.1/dist/svg-pan-zoom.min.js"></script>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'base',
                themeVariables: {{
                    background: '#f8fafc',
                    primaryColor: '#0f172a',
                    primaryTextColor: '#f8fafc',
                    primaryBorderColor: '#0072ff',
                    lineColor: '#64748b',
                    secondaryColor: '#1e293b',
                    tertiaryColor: '#e2e8f0',
                    mainBkg: '#0f172a',
                    nodeBorder: '#00c6ff',
                    clusterBkg: '#f8fafc',
                    clusterBorder: '#cbd5e1',
                    edgeColor: '#3b82f6',
                    fontFamily: 'Inter, sans-serif'
                }}
            }});
            
            document.addEventListener("DOMContentLoaded", async () => {{
                try {{
                    const {{ svg }} = await mermaid.render('mermaid-svg', `{safe_mermaid_code}`);
                    document.getElementById('mermaid-container').innerHTML = svg;
                    
                    // Add Pan/Zoom capabilities to the generated SVG
                    const svgElement = document.querySelector('#mermaid-container svg');
                    if(svgElement) {{
                        // Inject colorful linear gradients for nodes
                        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
                        defs.innerHTML = `
                            <linearGradient id="blue-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#00c6ff" />
                                <stop offset="100%" stop-color="#0072ff" />
                            </linearGradient>
                            <linearGradient id="green-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#11998e" />
                                <stop offset="100%" stop-color="#38ef7d" />
                            </linearGradient>
                        `;
                        svgElement.insertBefore(defs, svgElement.firstChild);
                        
                        // Classify backend nodes programmatically for multiple colors
                        const nodes = svgElement.querySelectorAll('.node');
                        nodes.forEach(node => {{
                            const text = node.textContent.toLowerCase();
                            if(text.includes('backend') || text.includes('service') || text.includes('api')) {{
                                node.classList.add('backend-node');
                            }}
                        }});

                        svgElement.setAttribute('id', 'flowchart-svg');
                        svgElement.style.width = "100%";
                        svgElement.style.height = "100%";
                        svgElement.style.maxWidth = "none";
                        
                        svgPanZoom('#flowchart-svg', {{
                            zoomEnabled: true,
                            controlIconsEnabled: true,
                            fit: true,
                            center: true,
                            minZoom: 0.1,
                            maxZoom: 20
                        }});
                    }}
                    
                    document.getElementById('download-btn').onclick = () => {{
                        const blob = new Blob([svg], {{ type: 'image/svg+xml' }});
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'architecture_flowchart.svg';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    }};
                }} catch (e) {{
                    document.getElementById('mermaid-container').innerHTML = '<p style="color:red">Error rendering flowchart: ' + e.message + '</p>';
                }}
            }});
        </script>
        <style>
            html, body {{
                margin: 0;  
                padding: 0;
                height: 100%;
                width: 100%;
                overflow: hidden; /* Prevent iframe scrollbars, let pan-zoom handle it */
                background-color: #f8fafc !important;
            }}
            .download-btn {{
                position: absolute;
                top: 10px;
                left: 10px;
                z-index: 1000;
                padding: 8px 16px;
                background-color: #0072ff;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-family: sans-serif;
                font-weight: 600;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.1s, background-color 0.2s;
            }}
            .download-btn:hover {{
                background-color: #00c6ff;
                transform: translateY(-1px);
            }}
            #mermaid-container {{
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #f8fafc !important;
            }}
            /* Colorful SVG Mermaid Overrides */
            .node rect, .node circle, .node polygon {{
                fill: url(#blue-gradient) !important;
                stroke: #0056cc !important;
                stroke-width: 1.5px !important;
            }}
            .node.backend-node rect, .node.backend-node circle, .node.backend-node polygon {{
                fill: url(#green-gradient) !important;
                stroke: #0f766e !important;
            }}
            .node .label, .node text {{
                fill: #ffffff !important;
                color: #ffffff !important;
                font-weight: 600 !important;
                font-family: 'Inter', sans-serif !important;
            }}
            .cluster rect {{
                fill: rgba(0, 114, 255, 0.04) !important;
                stroke: #00c6ff !important;
                stroke-width: 2px !important;
                stroke-dasharray: 4,4;
                rx: 12px;
                ry: 12px;
            }}
            .cluster .label {{
                fill: #0072ff !important;
                color: #0072ff !important;
                font-weight: bold !important;
            }}
            .edgePath .path {{
                stroke: #0072ff !important;
                stroke-width: 2.5px !important;
            }}
            .edgePath .markerPath {{
                fill: #0072ff !important;
            }}
            .edgeLabel, .edgeLabel span {{
                color: #1e293b !important;
                background-color: #f8fafc !important;
                font-weight: 600 !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 0.85rem !important;
            }}
        </style>
    </head>
    <body>
        <button id="download-btn" class="download-btn">📥 Download SVG</button>
        <div id="mermaid-container">
            <div style="font-family: sans-serif; color: #64748b; font-weight: bold;">Loading Interactive Diagram...</div>
        </div>
    </body>
    </html>
    """
    components.html(html_code, height=600, scrolling=False)

# --- Main Area ---
# Check if the URL matches the one that was actually analyzed
if st.session_state.summary and st.session_state.vectordb:
    if repo_url_input != st.session_state.repo_url:
        st.warning(f"You have changed the URL to **{repo_url_input}** but haven't analyzed it yet. Please click **Analyze Repository** in the sidebar to begin.")
    else:
        # Custom Premium Navigation Tabs
        col_tab1, col_tab2, col_tab3 = st.columns(3)
        with col_tab1:
            if st.button("📊 Dashboard & Flow", use_container_width=True, type="primary" if st.session_state.active_tab == "📊 Dashboard & Flow" else "secondary"):
                st.session_state.active_tab = "📊 Dashboard & Flow"
                st.rerun()
        with col_tab2:
            if st.button("📂 Code Explorer", use_container_width=True, type="primary" if st.session_state.active_tab == "📂 Code Explorer" else "secondary"):
                st.session_state.active_tab = "📂 Code Explorer"
                st.rerun()
        with col_tab3:
            if st.button("💬 Codebase Chat", use_container_width=True, type="primary" if st.session_state.active_tab == "💬 Codebase Chat" else "secondary"):
                st.session_state.active_tab = "💬 Codebase Chat"
                st.rerun()
        
        st.divider()

        # Render active tab
        if st.session_state.active_tab == "📊 Dashboard & Flow":
            # Show Metrics Cards for the repository
            st.subheader("📊 Repository Analysis Stats")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric(label="Cognitive Engine", value=st.session_state.selected_model)
            with m_col2:
                st.metric(label="Vector Store", value="ChromaDB")
            with m_col3:
                st.metric(label="RAG Pipeline Status", value="Ready 🟢")
            
            st.divider()

            # Display the summary and Flow Diagram
            # Try to extract and visually render the Mermaid code block
            mermaid_code = None
            clean_summary = st.session_state.summary
            
            # 1. Try explicit mermaid block
            mermaid_match = re.search(r'```mermaid(.*?)```', st.session_state.summary, re.DOTALL | re.IGNORECASE)
            if mermaid_match:
                mermaid_code = mermaid_match.group(1).strip()
                # Remove the mermaid block from the summary text so it doesn't render twice
                clean_summary = re.sub(r'## 📊 Architecture Flowchart\s*```mermaid.*?```', '', clean_summary, flags=re.DOTALL | re.IGNORECASE)
                clean_summary = re.sub(r'```mermaid.*?```', '', clean_summary, flags=re.DOTALL | re.IGNORECASE)
            else:
                # 2. Try ANY code block containing graph or flowchart
                blocks = re.findall(r'```(.*?)```', st.session_state.summary, re.DOTALL)
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
                        
            # 3. Ultimate Fallback: AI didn't use backticks at all!
            if not mermaid_code:
                match = re.search(r'(?:graph|flowchart)\s+(?:TD|LR|TB|BT|RL).*', st.session_state.summary, re.DOTALL | re.IGNORECASE)
                if match:
                    mermaid_code = match.group(0).strip()
                    
            # Display the cleaned summary text (without the raw mermaid block)
            st.markdown(clean_summary)
                    
            if mermaid_code:
                # Fix common LLM arrow syntax mistakes like "-->|text|> Node" or "-->|text|>Node"
                mermaid_code = re.sub(r'\|>\s*', '| ', mermaid_code)

                # Split multiple connections on the same line into separate lines (e.g. A --> B B --> C)
                mermaid_code = re.sub(r'(?<=\]|\)|\}|\w)\s+(\b\w+)\s*(-->|-.->|==>)', r'\n\1 \2', mermaid_code)

                # Ensure a valid Mermaid diagram header exists (default to flowchart TD if not present)
                stripped_code = mermaid_code.strip()
                if not (stripped_code.startswith("flowchart") or stripped_code.startswith("graph") or stripped_code.startswith("sequenceDiagram") or stripped_code.startswith("classDiagram") or stripped_code.startswith("stateDiagram") or stripped_code.startswith("erDiagram") or stripped_code.startswith("gantt") or stripped_code.startswith("pie") or stripped_code.startswith("gitGraph")):
                    mermaid_code = "flowchart TD\n" + mermaid_code

                # Programmatically strip style definitions (classDef, class, style) to prevent parsing crashes
                # and sanitize node labels line by line to handle nested quotes and ignore link labels
                clean_lines = []
                for line in mermaid_code.split('\n'):
                    stripped = line.strip()
                    if stripped.startswith('classDef') or stripped.startswith('style') or stripped.startswith('class '):
                        continue
                    
                    # 1. Temporarily hide link labels enclosed in pipes |...| to avoid corrupting them
                    placeholders = []
                    def hide_label(match):
                        placeholders.append(match.group(0))
                        return f"__LABEL_{len(placeholders)-1}__"
                    
                    temp_line = re.sub(r'\|([^|]+)\|', hide_label, line)
                    
                    # 2. Match shapes and wrap inner label in clean double-quotes
                    # Enforce preceding context limiters (line start, arrow, pipe, semicolon) to avoid
                    # matching function calls inside already-quoted strings (e.g. Parser(PyPDF2))
                    def repl_shape(match):
                        preceding = match.group(1)
                        node_id = match.group(2)
                        shape_start = match.group(3)
                        label = match.group(4)
                        shape_end = match.group(5)
                        clean_label = label.replace('"', '').replace("'", "")
                        return f'{preceding}{node_id}{shape_start}"{clean_label}"{shape_end}'
                    
                    # Run replacements (most specific to least specific)
                    # Preceding context pattern: (^|-->|-.->|==>|---|---|\||;)\s*
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\[\[)\s*(.*?)\s*(\]\])', repl_shape, temp_line)
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\(\[)\s*(.*?)\s*(\]\))', repl_shape, temp_line)
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\[\()\s*(.*?)\s*(\)\])', repl_shape, temp_line)
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\(\()\s*(.*?)\s*(\)\))', repl_shape, temp_line)
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\[)\s*(.*?)\s*(\])', repl_shape, temp_line)
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\()\s*(.*?)\s*(\))', repl_shape, temp_line)
                    temp_line = re.sub(r'(^|-->|-.->|==>|---|---|\||;)\s*(\b\w+)\s*(\{)\s*(.*?)\s*(\})', repl_shape, temp_line)
                    
                    # 3. Restore hidden link labels
                    for idx, placeholder in enumerate(placeholders):
                        temp_line = temp_line.replace(f"__LABEL_{idx}__", placeholder)
                        
                    clean_lines.append(temp_line)
                    
                mermaid_code = '\n'.join(clean_lines)

                st.divider()
                st.subheader("Visual Flow Diagram")
                render_mermaid(mermaid_code)
            else:
                st.warning("No flow diagram code was generated by the AI. Please click 'Analyze Repository' again.")

        elif st.session_state.active_tab == "📂 Code Explorer":
            st.subheader("📂 Interactive Codebase Explorer")
            st.write("Browse supported files in the cloned repository and run instant AI actions.")
            
            from backend.services.chunker import SUPPORTED_EXTENSIONS, IGNORE_FOLDERS
            
            def get_repository_files(repo_path):
                repo_files = []
                for root, dirs, files in os.walk(repo_path):
                    dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
                    for file in files:
                        if file.endswith(SUPPORTED_EXTENSIONS):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, repo_path)
                            repo_files.append((rel_path, full_path))
                return sorted(repo_files, key=lambda x: x[0])
                
            if st.session_state.repo_path and os.path.exists(st.session_state.repo_path):
                repo_files = get_repository_files(st.session_state.repo_path)
                if repo_files:
                    file_options = [rf[0] for rf in repo_files]
                    selected_file_rel = st.selectbox("Select file to explore", options=file_options)
                    selected_file_abs = next(rf[1] for rf in repo_files if rf[0] == selected_file_rel)
                    
                    try:
                        with open(selected_file_abs, "r", encoding="utf-8") as f:
                            file_content = f.read()
                            
                        st.info(f"📂 `{selected_file_rel}` | 📏 Size: {len(file_content)} characters | Lines: {len(file_content.splitlines())}")
                        
                        ext = os.path.splitext(selected_file_rel)[1]
                        lang_map = {
                            ".py": "python",
                            ".js": "javascript",
                            ".ts": "typescript",
                            ".java": "java",
                            ".cpp": "cpp",
                            ".md": "markdown"
                        }
                        st.code(file_content, language=lang_map.get(ext, "text"), line_numbers=True)
                        
                        st.write("⚡ **One-Click AI Actions:**")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("🔍 Explain Code", use_container_width=True):
                                st.session_state.pending_query = f"Explain what the code in file `{selected_file_rel}` does in detail, focusing on its role and key classes/functions."
                                st.session_state.active_tab = "💬 Codebase Chat"
                                st.rerun()
                        with c2:
                            if st.button("🧪 Generate Unit Tests", use_container_width=True):
                                st.session_state.pending_query = f"Generate comprehensive unit tests for the code in file `{selected_file_rel}`."
                                st.session_state.active_tab = "💬 Codebase Chat"
                                st.rerun()
                        with c3:
                            if st.button("🧹 Audit for Bugs", use_container_width=True):
                                st.session_state.pending_query = f"Analyze the code in file `{selected_file_rel}` for security flaws, code quality issues, or potential bugs."
                                st.session_state.active_tab = "💬 Codebase Chat"
                                st.rerun()
                    except Exception as e:
                        st.error(f"Could not read file: {e}")
                else:
                    st.warning("No supported source code files found in this repository.")
            else:
                st.error("Repository directory not found on disk. Please re-run analysis in the sidebar Setup.")

        elif st.session_state.active_tab == "💬 Codebase Chat":
            st.subheader("💬 Ask Questions About the Codebase")
            
            # Quick-action prompt buttons
            st.write("💡 **Quick Queries:**")
            cols = st.columns(3)
            with cols[0]:
                if st.button("🔍 Explain Core Flow", use_container_width=True):
                    st.session_state.pending_query = "Explain the core execution flow of this repository."
                    st.rerun()
            with cols[1]:
                if st.button("🛠️ List Dependencies", use_container_width=True):
                    st.session_state.pending_query = "What are the main libraries, databases, and dependencies used in this project?"
                    st.rerun()
            with cols[2]:
                if st.button("🚀 Error Handling Structure", use_container_width=True):
                    st.session_state.pending_query = "Explain how error handling is structured in this repository."
                    st.rerun()

            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # --- Global Chat Input & Execution (Floats at bottom globally) ---
        user_query = st.chat_input("Ask a question about the codebase...")
        
        # Execute query if we have input from chat_input or a redirection action
        active_query = None
        if user_query:
            active_query = user_query
        elif st.session_state.pending_query:
            active_query = st.session_state.pending_query
            st.session_state.pending_query = None
            
        if active_query:
            # Shift focus to chat tab and append user query
            st.session_state.active_tab = "💬 Codebase Chat"
            st.session_state.chat_history.append({"role": "user", "content": active_query})
            
            with st.spinner("Searching codebase..."):
                try:
                    response = ask_question(
                        st.session_state.vectordb, 
                        active_query,
                        model_name=st.session_state.selected_model,
                        temperature=st.session_state.llm_temperature
                    )
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    err_msg = str(e)
                    if "RESOURCE_EXHAUSTED" in err_msg:
                        response = "⚠️ **API Rate Limit Exceeded (429)**. Please wait a moment and try again."
                    else:
                        response = f"⚠️ **Error generating response**: {err_msg}"
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            st.rerun()

        # Render Footer inline at the bottom of the main scroll container
        st.markdown("""
        <div class="footer">
            <span>CodeMind AI</span> • Enterprise-grade Codebase Architect & Knowledge Platform<br>
            <small>© 2026 CodeMind AI. All rights reserved.</small>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("👈 Please enter a GitHub Repository URL in the sidebar and click **Analyze Repository** to begin.")
    
    # Render Footer inline at the bottom of the main scroll container
    st.markdown("""
    <div class="footer">
        <span>CodeMind AI</span> • Enterprise-grade Codebase Architect & Knowledge Platform<br>
        <small>© 2026 CodeMind AI. All rights reserved.</small>
    </div>
    """, unsafe_allow_html=True)
