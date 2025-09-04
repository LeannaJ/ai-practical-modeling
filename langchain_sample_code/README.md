# LangChain Sample Code

This folder contains Jupyter notebooks demonstrating simple Retrieval-Augmented Generation (RAG) workflows using LangChain. The notebooks progress from a minimal setup to experiments with LangSmith for tracing and evaluation.

## Contents
- `1_rag_simpler.ipynb`: Minimal RAG pipeline demo
- `2_rag_simpler.ipynb`: Slightly expanded indexing and retrieval settings
- `3_rag_simpler_langsmith.ipynb`: Intro to LangSmith for experiment tracking
- `4_rag_simpler_langsmith.ipynb`: Advanced LangSmith usage (tracing/evaluation)
- `5_rag_simpler_langsmith.ipynb`: Prompt/retriever variations and quick comparisons

## Prerequisites
- Python 3.10+
- A virtual environment is recommended
- Install dependencies as needed. If you want a quick start, you can reuse packages used in the RAG examples:
```bash
pip install -r ../rag:qrag/requirements.txt
```
(or install packages cell-by-cell inside the notebooks.)

## Optional: LangSmith
If you plan to use LangSmith, set the following environment variables:
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
export LANGCHAIN_API_KEY=your_langsmith_api_key
export LANGCHAIN_PROJECT=your_project_name
```

## How to Run
1. Open any `.ipynb` in VS Code, Jupyter Lab, or Notebook.
2. Execute cells from top to bottom: build embeddings/index → run retriever → call the LLM → review responses.
3. Tweak prompt or retriever parameters (e.g., `k`, `score_threshold`) and compare results.

## Tips
- Start with a small document set before scaling to your real data.
- Periodically clear caches/temporary artifacts to keep runs consistent.
- With LangSmith on, experiment comparison and regression detection become much easier.

## References
- LangChain Docs: https://python.langchain.com
- LangSmith: https://smith.langchain.com
