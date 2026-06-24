import os

# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from groq import RateLimitError, AuthenticationError


def get_llm(model_name=None, temperature=0.2):
    """Return an LLM instance. Auto-selects model and falls back between providers."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    # Auto-select model when none specified — prefer Groq, fallback to Gemini
    if not model_name:
        if groq_api_key:
            model_name = "llama-3.3-70b-versatile"
        elif gemini_api_key:
            model_name = "gemini-2.0-flash"
        else:
            raise ValueError(
                "No API key found. Please set GROQ_API_KEY or GEMINI_API_KEY in your .env file."
            )

    # If a gemini model was requested but no Gemini key, fall back to Groq
    if model_name.startswith("gemini-"):
        if gemini_api_key:
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=gemini_api_key,
                max_retries=2,
            )
        elif groq_api_key:
            # Gemini key missing — silently fall back to Groq
            return ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                max_retries=2,
                groq_api_key=groq_api_key,
            )
        else:
            raise ValueError(
                "No API key found. Please set GROQ_API_KEY or GEMINI_API_KEY in your .env file."
            )
    else:
        if groq_api_key:
            return ChatGroq(
                model=model_name,
                temperature=temperature,
                max_retries=2,
                groq_api_key=groq_api_key,
            )
        elif gemini_api_key:
            # Groq key missing — silently fall back to Gemini
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=temperature,
                google_api_key=gemini_api_key,
                max_retries=2,
            )
        else:
            raise ValueError(
                "No API key found. Please set GROQ_API_KEY or GEMINI_API_KEY in your .env file."
            )


def _extract_text(response) -> str:
    """Extract plain text from an LLM response, handling list-of-blocks format."""
    content = response.content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def _invoke_llm(llm, prompt: str, model_name: str | None, temperature: float) -> str:
    """
    Invoke an LLM with full error handling and automatic fallback:
      - Groq AuthenticationError  → friendly message
      - Groq RateLimitError       → fallback to Gemini (if key available)
      - Gemini RESOURCE_EXHAUSTED → fallback to Groq  (if key available)
      - All other exceptions      → friendly message
    Returns the response text string on success.
    """
    try:
        response = llm.invoke(prompt)
        return _extract_text(response)

    except AuthenticationError:
        return (
            "Error: Invalid Groq API key. "
            "Please check your GROQ_API_KEY in the .env file."
        )

    except RateLimitError:
        groq_key = os.getenv("GROQ_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        # First try: switch to llama-3.1-8b-instant (20k TPM — 3x higher limit)
        if groq_key and model_name != "llama-3.1-8b-instant":
            try:
                fallback_llm = ChatGroq(
                    model="llama-3.1-8b-instant",
                    temperature=temperature,
                    max_retries=2,
                    groq_api_key=groq_key,
                )
                response = fallback_llm.invoke(prompt)
                return _extract_text(response)
            except RateLimitError:
                pass  # Also rate-limited — try Gemini next
            except Exception as fe:
                return f"Error: Groq fallback model also failed: {fe}"

        # Second try: fall back to Gemini
        if gemini_key:
            try:
                fallback_llm = get_llm(model_name="gemini-2.0-flash", temperature=temperature)
                response = fallback_llm.invoke(prompt)
                return _extract_text(response)
            except Exception as fe:
                return (
                    f"Error: Groq rate limit exceeded and Gemini fallback also failed: {fe}. "
                    "Please wait a few minutes and try again."
                )

        return (
            "Error: Groq rate limit exceeded. "
            "Please wait 1-2 minutes and try again. "
            "Tip: Add GEMINI_API_KEY to your .env for automatic fallback."
        )

    except Exception as e:
        err_str = str(e)

        # Gemini quota exhausted (free-tier daily/minute limit)
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key:
                try:
                    fallback_llm = get_llm(
                        model_name="llama-3.3-70b-versatile", temperature=temperature
                    )
                    response = fallback_llm.invoke(prompt)
                    return _extract_text(response)
                except Exception as fe:
                    return (
                        f"Error: Gemini quota exhausted. "
                        f"Groq fallback also failed: {fe}."
                    )
            return (
                "Error: Your Gemini free-tier quota is exhausted. "
                "Add a GROQ_API_KEY to your .env file for automatic fallback, "
                "or wait until tomorrow for the Gemini quota to reset."
            )

        # Any other unexpected error
        return f"Error: An unexpected error occurred — {err_str}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask_question(vectordb, question: str, model_name: str | None = None, temperature: float = 0.2) -> str:
    """Answer a question about the indexed repository using RAG."""
    docs = vectordb.similarity_search(question, k=5)
    context = "\n\n".join(doc.page_content for doc in docs)

    try:
        llm = get_llm(model_name=model_name, temperature=temperature)
    except ValueError as e:
        return f"Error: {e}"

    prompt = f"""
You are an expert software architect.

Repository Context:
{context}

Question:
{question}

Answer based only on the repository context.
"""
    return _invoke_llm(llm, prompt, model_name, temperature)


def generate_repo_summary(vectordb, model_name: str | None = None, temperature: float = 0.2) -> str:
    """Generate a detailed architectural summary of the indexed repository."""
    summary_question = (
        "Explain the detailed architecture, list the tools and frameworks used, "
        "provide a high-level overview of how this project works, and create a "
        "highly detailed mermaid flowchart of the architecture showing specific "
        "directories and modules."
    )
    docs = vectordb.similarity_search(summary_question, k=8)
    context = "\n\n".join(doc.page_content for doc in docs)

    try:
        llm = get_llm(model_name=model_name, temperature=temperature)
    except ValueError as e:
        return f"Error: {e}"

    prompt = f"""
You are an expert software architect analyzing a new codebase.
Using the provided repository context, create a comprehensive overview of the system architecture and its sequential runtime execution flow.

CRITICAL INSTRUCTION: You are analyzing a USER-SUPPLIED repository. DO NOT mention or reference CodeMind-AI, FastAPI, or any repository analyzer tool. Focus ONLY on the repository being analyzed based on the file paths and content provided in the context.

Structure your response exactly as follows:

## 🏗 Architecture
(Provide an extremely detailed, professional breakdown of the high-level architecture, module design, and file structure. Use formatted bullet points and ensure there is a blank line between each point for readability. Explain exactly how the major components interact with each other.)

## 📊 Architecture Flowchart
(Provide a highly detailed, professional Mermaid flowchart diagram wrapped in a ```mermaid code block.
CRITICAL RULES FOR THE FLOWCHART:
- It MUST represent the step-by-step runtime workflow and execution sequence of the repository's main files and functions, tracing from the initial trigger (e.g., User Interaction / API endpoint trigger) through processing logic, to the final outputs/returns.
- Do NOT show static module relationships or abstract class hierarchies. Instead, design a logical flow of actions (e.g., frontend/app.py --"1. Submits Input"--> backend/api.py --"2. Queries DB"--> backend/db.py --"3. Returns Data"--> frontend/app.py).
- Keep focus strictly on the project's custom files, functions, and directories. Do NOT add nodes for external databases (like SQLite, PostgreSQL), APIs, libraries, or developer tools. If you need to mention database queries or API calls, show them as labels on the edges/transitions between custom project modules, rather than as separate boxes.
- Write strict Mermaid v10+ syntax:
  1. Define all nodes and their labels separately at the top of the chart (e.g., A[Label A], B[Label B]).
  2. Use simple, short node IDs (A, B, C, D) and connect them on separate lines (e.g., A --> B).
  3. One connection per line. Do NOT write multiple node definitions or inline labels with connections (never write A[Label] --> B[Label]).
  4. Replace all parentheses () inside node labels with hyphens (e.g. B[PDF Parser - PyPDF2] instead of B[PDF Parser (PyPDF2)]).
  5. Never use double or single quotes inside node labels.)

## 🛠 Tools & Frameworks
(List ALL key tools, libraries, and frameworks detected. Format this as a bulleted list. For EACH tool, write a detailed 2-3 sentence explanation of EXACTLY why it was chosen and the specific role it plays. Leave a blank line between each tool.)

## ⚙️ How it Works
(Provide an exhaustive, step-by-step technical walkthrough of the core functionality. Break down the execution flow from start to finish using numbered lists or bullet points. Leave a blank empty line between each step so that the text is not compressed together.)

Repository Context:
{context}

If the context is insufficient, provide the best possible estimate based on common practices, but note that the context was limited.
"""
    return _invoke_llm(llm, prompt, model_name, temperature)
