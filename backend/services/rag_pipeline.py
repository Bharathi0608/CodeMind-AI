import os
# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI   
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
from groq import RateLimitError, AuthenticationError

def get_llm(model_name=None, temperature=0.2):
    groq_api_key = os.getenv("GROQ_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    # If no model is selected, fallback automatically
    if not model_name:
        if groq_api_key:
            model_name = "llama-3.3-70b-versatile"
        elif gemini_api_key:
            model_name = "gemini-2.0-flash"
        else:
            raise ValueError("No API key found. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file.")
            
    if model_name.startswith("gemini-"):
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_retries=5
        )
    else:
        return ChatGroq(
            model=model_name,
            temperature=temperature,
            max_retries=5,
            groq_api_key=groq_api_key
        )

def ask_question(vectordb, question, model_name=None, temperature=0.2):
    docs = vectordb.similarity_search(
        question,
        k=5
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    try:
        llm = get_llm(model_name=model_name, temperature=temperature)
    except ValueError:
        return "Error: No API key found. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file."

    prompt = f"""

You are an expert software architect.

Repository Context:
{context}   

Question:
{question}  

Answer based only on the repository context.
"""
    
    try:
        response = llm.invoke(prompt)
    except AuthenticationError:
        return "Error: Invalid API key. Please check your GROQ_API_KEY in the .env file."
    except RateLimitError:
        # Fallback to Gemini if Groq rate limit is hit and Gemini API key is available
        if model_name and not model_name.startswith("gemini-") and os.getenv("GEMINI_API_KEY"):
            try:
                llm = get_llm(model_name="gemini-2.0-flash", temperature=temperature)
                response = llm.invoke(prompt)
            except Exception as e:
                return f"Error: Rate limit exceeded on Groq. Gemini fallback failed: {str(e)}. Please add GEMINI_API_KEY to your .env file or wait for Groq rate limit to reset."
        else:
            return "Error: Rate limit exceeded on Groq. Please add GEMINI_API_KEY to your .env file for automatic fallback, or wait a few minutes for the rate limit to reset."
    
    content = response.content
    if isinstance(content, list):
        text_content = ""
        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_content += block["text"]
            elif isinstance(block, str):
                text_content += block
        return text_content
        
    return str(content)

def generate_repo_summary(vectordb, model_name=None, temperature=0.2):
    summary_question = "Explain the detailed architecture, list the tools and frameworks used, provide a high-level overview of how this project works, and create a highly detailed mermaid flowchart of the architecture showing specific directories and modules."
    docs = vectordb.similarity_search(
        summary_question,
        k=30
    )

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    try:
        llm = get_llm(model_name=model_name, temperature=temperature)
    except ValueError:
        return "Error: No API key found. Please set GROQ_API_KEY or GEMINI_API_KEY in .env file."

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
    
    try:
        response = llm.invoke(prompt)
    except AuthenticationError:
        return "Error: Invalid API key. Please check your GROQ_API_KEY in the .env file."
    except RateLimitError:
        # Fallback to Gemini if Groq rate limit is hit and Gemini API key is available
        if model_name and not model_name.startswith("gemini-") and os.getenv("GEMINI_API_KEY"):
            try:
                llm = get_llm(model_name="gemini-2.0-flash", temperature=temperature)
                response = llm.invoke(prompt)
            except Exception as e:
                return f"Error: Rate limit exceeded on Groq. Gemini fallback failed: {str(e)}. Please add GEMINI_API_KEY to your .env file or wait for Groq rate limit to reset."
        else:
            return "Error: Rate limit exceeded on Groq. Please add GEMINI_API_KEY to your .env file for automatic fallback, or wait a few minutes for the rate limit to reset."
    
    # In newer langchain/gemini versions, content can sometimes be a list of blocks
    content = response.content
    if isinstance(content, list):
        text_content = ""
        for block in content:
            if isinstance(block, dict) and "text" in block:
                text_content += block["text"]
            elif isinstance(block, str):
                text_content += block
        return text_content
    
    return str(content)
