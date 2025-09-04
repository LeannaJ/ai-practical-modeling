# AI Practical Modeling

A collection of hands-on, minimal-yet-useful projects for applied AI/LLM work. Each folder is an independent, practical modeling example. New practical folders will be appended to the list below over time.

## Projects

### 1) `ai_agent_newsbot`
A lightweight news-summarization agent. Given sources and configuration, it aggregates recent articles and produces concise summaries. Useful as a template for automation-style agents (config + run → structured output).
- Tech: Python, simple agent loop, configurable prompts
- Quick start: see `ai_agent_newsbot/README.md`

### 2) `langchain_sample_code`
A set of Jupyter notebooks demonstrating Retrieval-Augmented Generation (RAG) with LangChain, from a minimal pipeline to LangSmith-based tracing/evaluation.
- Tech: LangChain, (optional) LangSmith, Python notebooks
- Quick start: see `langchain_sample_code/README.md`

### 3) `rag:qrag`
A practical RAG/Q&A prototype over PDF content: parse → chunk → embed → store → retrieve → generate answers.
- Tech: Python, embeddings/vector store, PDF processing
- Quick start: see `rag:qrag/README.md`

## Contributing / Adding New Practical Folders
- Add a new top-level folder with a clear, focused objective (e.g., "<domain>_<task>").
- Include a short `README.md` describing purpose, setup, and how to run.
- Append a brief one-liner to the list above in this root `README.md`.

