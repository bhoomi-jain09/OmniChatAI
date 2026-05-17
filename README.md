# OmniChat AI 🤖
### An Intelligent Multi-Tool Chatbot Powered by LangChain, LangGraph & Streamlit

OmniChat AI is a feature-rich, persistent conversational AI assistant built with LangChain and LangGraph for orchestration, and Streamlit for the frontend. It combines PDF-based RAG (Retrieval-Augmented Generation), live web search, real-time stock prices, a calculator, and SQL-backed persistent memory — all in one unified chat interface.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
  - [Persistent Memory](#persistent-memory)
  - [PDF Upload & RAG](#pdf-upload--rag)
  - [Web Search Tool](#web-search-tool)
  - [Stock Price Tool](#stock-price-tool)
  - [Calculator Tool](#calculator-tool)
  - [Conversation Threads](#conversation-threads)
- [Project Structure](#project-structure)
- [Customizing the Agent](#customizing-the-agent)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Persistent SQL Memory** — Conversations are stored in a SQL database so the chatbot never loses context, regardless of when or how often you chat. Memory persists across sessions and restarts.
- **PDF RAG System** — Upload one or more PDF files and ask questions about their content. Documents are chunked, embedded, and stored in a vector store for semantic retrieval at query time.
- **Web Search Tool (DuckDuckGo)** — The agent can search the live web using DuckDuckGo to answer questions about current events, news, and real-time information beyond its training data.
- **Stock Price Tool** — Fetch real-time or recent stock prices for any ticker symbol directly within the chat.
- **Calculator Tool** — Perform mathematical calculations as part of the conversation, including arithmetic, algebra, and unit conversions.
- **Conversation Threads** — Each chat session is stored as a separate thread, allowing you to revisit, switch between, and manage multiple independent conversations.
- **LangGraph Agent Orchestration** — The agent uses a LangGraph state machine to intelligently route queries to the right tool or retriever and stream responses back to the UI.
- **Streamlit Frontend** — Clean, responsive web interface built with Streamlit — no separate frontend build step required.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                           │
│  - Chat UI          - PDF Upload        - Thread Switcher        │
└────────────────────────────┬─────────────────────────────────────┘
                             │ User Input / File Upload
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│               LangGraph Agent (Orchestration Layer)              │
│                                                                  │
│   ┌───────────┐  ┌──────────────┐  ┌───────────┐  ┌─────────┐  │
│   │ PDF RAG   │  │  Web Search  │  │  Stock    │  │  Calc   │  │
│   │ Retriever │  │ (DuckDuckGo) │  │  Price    │  │  Tool   │  │
│   └─────┬─────┘  └──────┬───────┘  └─────┬─────┘  └────┬────┘  │
│         └───────────────┴────────────────┴──────────────┘       │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │   LLM (via      │                           │
│                    │   LangChain)    │                           │
│                    └────────┬────────┘                           │
└─────────────────────────────┼────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌────────────┐  ┌──────────────┐  ┌──────────────┐
     │ SQL Memory │  │ Vector Store │  │  Thread DB   │
     │  (SQLite / │  │ (Embeddings) │  │  (per-user   │
     │ PostgreSQL)│  │              │  │  sessions)   │
     └────────────┘  └──────────────┘  └──────────────┘
```

The system consists of three main layers:

**Frontend (Streamlit)** — Provides the chat UI, PDF upload widget, thread management sidebar, and real-time streaming of agent responses.

**Agent Layer (LangChain + LangGraph)** — A LangGraph state machine that routes user queries to the appropriate tools (RAG, web search, stock prices, calculator), calls the LLM, and returns streamed responses.

**Persistence Layer (SQL + Vector Store)** — A SQL database stores full conversation history per thread so memory is never lost. A vector store holds PDF embeddings for semantic retrieval.

---

## Prerequisites

- Python 3.10+
- An GroqAI API key (or another LangChain-compatible LLM provider)
- `pip` or a virtual environment manager (e.g. `venv`, `conda`)
- Optional: A LangSmith API key for tracing and debugging

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/omnichat-ai.git
cd omnichat-ai
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

---

## Environment Variables

Create a `.env` file at the project root with the following variables:

```env
# ── LLM Provider ──────────────────────────────────────────────────
GROQAI_API_KEY=your-groqqai-api-key-here

# ── Vector Store ──────────────────────────────────────────────────
# Path or connection string for your vector store
VECTOR_STORE_PATH=./data/vectorstore

# ── SQL Memory & Thread Storage ───────────────────────────────────
# SQLite (default, no extra setup):
DATABASE_URL=sqlite:///./data/omnichat_memory.db

# PostgreSQL (optional, for production):
# DATABASE_URL=postgresql://user:password@localhost:5432/omnichat

# ── Stock Price Tool ──────────────────────────────────────────────
# If using a paid stock API, add your key here. 
# The default implementation uses a free provider.
STOCK_API_KEY=your-stock-api-key-here   # optional

# ── LangSmith Tracing (Optional but Recommended) ──────────────────
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key-here
LANGCHAIN_PROJECT=omnichat-ai
```

**Variable reference:**

- `OPENAI_API_KEY` — Your LLM provider's API key. Required.
- `VECTOR_STORE_PATH` — Where PDF embeddings are persisted on disk.
- `DATABASE_URL` — SQLAlchemy connection string for SQL memory and thread storage. Defaults to a local SQLite file.
- `STOCK_API_KEY` — API key for the stock price provider (if your chosen provider requires one).
- `LANGCHAIN_TRACING_V2` — Set to `true` to enable LangSmith tracing for debugging agent steps.
- `LANGCHAIN_API_KEY` — Your LangSmith key (optional).
- `LANGCHAIN_PROJECT` — Project name as it appears in LangSmith.

---

## Running the App

Start the Streamlit app:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Usage Guide

### Persistent Memory

OmniChat AI stores every message in a SQL database linked to a conversation thread. This means:

- The chatbot remembers what you discussed yesterday, last week, or months ago.
- Restarting the app or closing your browser does **not** erase your history.
- Memory is retrieved at the start of each new message and injected into the agent's context window, so answers stay coherent across long gaps between sessions.

The memory system is implemented using LangChain's `SQLChatMessageHistory`, backed by SQLite (default) or PostgreSQL.

### PDF Upload & RAG

OmniChat AI supports uploading PDF documents and asking questions about their contents using Retrieval-Augmented Generation (RAG).

1. Click the **Upload PDF** button in the sidebar.
2. Select one or more PDF files (max 5 files, each under 20 MB).
3. The system will parse, chunk, embed, and store the document in the vector store.
4. Once ingestion is complete, simply ask questions — the agent will automatically retrieve relevant chunks and cite the source document in its answer.

PDFs are stored persistently in the vector store, so you only need to upload a document once.

### Web Search Tool

When you ask about current events, recent news, or any topic that benefits from live data, the agent automatically invokes the DuckDuckGo search tool to fetch up-to-date results before generating a response.

Examples of queries that trigger web search:
- "What happened in the news today?"
- "Latest updates on [topic]?"
- "Who won the [recent event]?"

No API key is required for DuckDuckGo search.

### Stock Price Tool

You can ask for real-time or recent stock prices directly in the chat. The agent will use the stock price tool to fetch the data and present it in a readable format.

Examples:
- "What is the current price of AAPL?"
- "Show me TSLA stock price."
- "How is GOOGL performing today?"

### Calculator Tool

The agent can solve math problems as part of a conversation. Just ask naturally:

- "What is 15% of 4,500?"
- "Calculate the compound interest on ₹1,00,000 at 8% for 5 years."
- "Convert 72 km/h to m/s."

### Conversation Threads

Threads allow you to maintain separate, independent conversations — similar to how ChatGPT manages chats in the sidebar.

- Every new chat session is automatically assigned a unique thread ID.
- All threads are listed in the **sidebar** so you can switch between them at any time.
- Switching threads loads the full message history for that thread from the SQL database.
- You can rename or delete threads from the sidebar.

Thread data is persisted in the SQL database alongside message memory.

---

## Project Structure

```
omnichat-ai/
│
├── app.py                        # Streamlit entry point
├── requirements.txt
├── .env.example
│
├── agent/
│   ├── graph.py                  # LangGraph state machine definition
│   ├── nodes.py                  # Graph nodes (router, responder, etc.)
│   └── tools/
│       ├── pdf_retriever.py      # RAG retrieval tool
│       ├── web_search.py         # DuckDuckGo search tool
│       ├── stock_price.py        # Stock price fetching tool
│       └── calculator.py         # Calculator tool
│
├── memory/
│   ├── sql_memory.py             # SQLChatMessageHistory setup
│   └── thread_manager.py         # Thread creation, listing, switching
│
├── ingestion/
│   └── pdf_ingestion.py          # PDF parsing, chunking, embedding
│
├── vectorstore/
│   └── store.py                  # Vector store init and retriever factory
│
├── config/
│   └── settings.py               # Centralised config and env loading
│
└── data/
    ├── omnichat_memory.db         # SQLite memory DB (auto-created)
    └── vectorstore/               # Persisted PDF embeddings
```

---

## Customizing the Agent

**Changing the LLM model** — Edit `config/settings.py` and update the `LLM_MODEL` variable to any LangChain-compatible model (e.g. `gpt-4o`, `claude-3-5-sonnet`, `mistral`).

**Adding a new tool** — Create a new file in `agent/tools/`, implement it as a LangChain `Tool` or `StructuredTool`, and register it in `agent/graph.py`.

**Adjusting RAG retrieval** — Change the chunk size, overlap, or number of retrieved documents (`k`) in `ingestion/pdf_ingestion.py` and `vectorstore/store.py`.

**Switching the vector store** — The default uses FAISS (local). You can swap in Chroma, Pinecone, or Supabase by updating `vectorstore/store.py`.

**Changing the memory database** — Update `DATABASE_URL` in your `.env` file to a PostgreSQL or MySQL connection string for production deployments.

**Modifying prompts** — Agent system prompts and tool descriptions live in `agent/nodes.py`. Adjust them to change the agent's tone, focus, or behaviour.

---

## Troubleshooting

**App won't start**
Make sure all dependencies are installed (`pip install -r requirements.txt`) and your `.env` file is present and correctly filled in.

**Memory not persisting between sessions**
Ensure `DATABASE_URL` in your `.env` points to a writable location. For SQLite, confirm the `data/` directory exists. Run `python -c "from memory.sql_memory import init_db; init_db()"` to manually initialise the schema.

**PDF ingestion fails**
Check that the PDF is not password-protected or corrupted. Files over 20 MB may need to be split before uploading.

**Web search returns no results**
DuckDuckGo rate-limits aggressive queries. If you hit limits, add a small delay between searches or switch to a different search backend in `agent/tools/web_search.py`.

**Stock price tool errors**
Verify your `STOCK_API_KEY` is set correctly. Check that the ticker symbol you're querying is valid (e.g. `AAPL`, `TSLA`, `RELIANCE.NS`).

**LangGraph not routing to the correct tool**
Enable LangSmith tracing (`LANGCHAIN_TRACING_V2=true`) to visualise each step of the graph and identify where routing goes wrong.

---

## License

MIT License. See `LICENSE` for details.
