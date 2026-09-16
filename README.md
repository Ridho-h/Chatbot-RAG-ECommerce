# 🛒 ShopAI — Production-Grade E-Commerce RAG Chatbot

An intelligent e-commerce chatbot powered by Retrieval-Augmented Generation (RAG), featuring a FastAPI backend, React frontend, RBAC authentication, and LangSmith tracing and LLM-as-a-judge evaluation.

![Architecture](https://img.shields.io/badge/Architecture-Production--Grade-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18-blue)

<div align="center">
  <img src="https://via.placeholder.com/800x450.gif?text=Your+Demo+GIF+Here" alt="ShopAI Demo" width="100%" />
</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🤖 RAG Chatbot** | ReAct agent with Pinecone vector search + web search |
| **🔐 RBAC Auth** | JWT-based authentication with admin/customer roles |
| **📊 Admin Dashboard** | Metrics, evaluation scores, re-ingestion controls |
| **📈 LangSmith Evaluation** | Automated LLM-as-a-judge evaluation against a Golden Dataset |
| **🔍 LangSmith Tracing** | Query traces, latency tracking, token cost monitoring |
| **💬 Multi-turn Memory** | Per-session conversation history with TTL cleanup |
| **🚦 Rate Limiting** | Configurable per-IP rate limiting |
| **📋 Structured Logging** | JSON logging with request IDs |
| **🐳 Docker Ready** | One-command deployment with Docker Compose |
| **💰 100% Free** | All components use free/open-source tools |

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────┐
│  React Frontend │────▶│  FastAPI Backend                      │
│  (Port 3000)    │     │  (Port 8000)                          │
│                 │     │                                       │
│                 │     │  ┌─────────┐  ┌──────────────────┐   │
│  • Chat UI      │     │  │ ReAct   │──│ Product DB Search │   │
│  • Login/Signup │     │  │ Agent   │  │ (Pinecone)        │   │
│  • Admin Panel  │     │  │ (Groq)  │  └──────────────────┘   │
│                 │     │  │         │  ┌──────────────────┐   │
│                 │     │  │         │──│ Web Search        │   │
│                 │     │  └─────────┘  │ (DuckDuckGo)      │   │
│                 │     │               └──────────────────┘   │
│                 │     │  ┌────────┐ ┌────────┐ ┌────────┐   │
│                 │     │  │ JWT    │ │ Rate   │ │ Memory │   │
│                 │     │  │ Auth   │ │ Limit  │ │ (TTL)  │   │
│                 │     │  └────────┘ └────────┘ └────────┘   │
└─────────────────┘     └──────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │  LangSmith       │
                   │  (Tracing/Eval)  │
                   └──────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Ridho-h/Chatbot-RAG-ECommerce.git
cd Chatbot-RAG-ECommerce

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys (at minimum: GROQ_API_KEY)

# 3. Start all services
docker-compose up --build

# 4. Open the app
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Login with: admin / admin123
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Ingest product data (first time only)
python scripts/ingest.py --download

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Opens at http://localhost:3000
```

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ | — | Groq API key for LLM |
| `LLM_PROVIDER` | — | `groq` | `groq` or `openai` |
| `LLM_MODEL_NAME` | — | `llama-3.3-70b-versatile` | Model name |
| `SEARCH_PROVIDER` | — | `duckduckgo` | `duckduckgo` (free) or `serper` |
| `PINECONE_API_KEY` | ✅ | — | Pinecone API key |
| `PINECONE_INDEX_NAME` | ✅ | `ecommerce-bot` | Pinecone Index name |
| `KAGGLE_USERNAME` | For ingestion | — | Kaggle credentials |
| `KAGGLE_KEY` | For ingestion | — | Kaggle API key |
| `JWT_SECRET_KEY` | ⚠️ Change! | `change-me...` | JWT signing secret |
| `ADMIN_USERNAME` | — | `admin` | Default admin username |
| `ADMIN_PASSWORD` | ⚠️ Change! | `admin123` | Default admin password |
| `LANGCHAIN_TRACING_V2` | — | `true` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | — | — | LangSmith API Key |
| `RATE_LIMIT_PER_MINUTE` | — | `30` | Rate limit per IP |

## 📊 LangSmith Evaluation

Run the evaluation script to measure RAG quality against a Golden Dataset using an LLM-as-a-judge:

```bash
docker exec chatbot-backend python scripts/langsmith_pipeline.py
```

Results are pushed directly to your LangSmith project dashboard under the `ecommerce-chatbot` project, allowing you to easily compare passes and fails.

## 🔍 LangSmith Tracing

Enable tracing to monitor query latency, token usage, and costs:

```bash
# Set in backend/.env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=ecommerce-chatbot
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

Access your traces at [https://smith.langchain.com](https://smith.langchain.com).

## 🔐 RBAC Roles

| Role | Permissions |
|------|-------------|
| **Customer** | Chat, view own sessions |
| **Admin** | All above + metrics dashboard, re-ingestion, eval results, session cleanup |

Default admin: `admin` / `admin123` (change via env vars in production!)

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI endpoints (chat, health, admin)
│   │   ├── auth/          # JWT, RBAC, user management
│   │   ├── core/          # RAG engine (LLM, vectorstore, agent, tools)
│   │   ├── data/          # Dataset loader
│   │   ├── middleware/    # Rate limiting, logging
│   │   └── schemas/       # Pydantic models
│   ├── scripts/           # CLI tools (ingest, evaluate)
│   ├── data/              # FAISS index, datasets
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React UI components
│   │   ├── hooks/         # useAuth, useChat
│   │   └── utils/         # API client
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── Chatbot_RAG_ECommerce.ipynb  # Original prototype
```

## 🛠️ API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | — | Create account |
| POST | `/api/auth/login` | — | Get JWT token |
| POST | `/api/chat` | ✅ | Send chat message |
| GET | `/api/admin/metrics` | Admin | View system metrics |
| POST | `/api/admin/ingest` | Admin | Re-ingest dataset |
| GET | `/api/admin/eval` | Admin | Get RAGAS results |
| GET | `/health` | — | Liveness check |
| GET | `/ready` | — | Readiness check |
| GET | `/docs` | — | Swagger UI |

## 💰 Cost

**This entire stack is 100% free for development and small-scale production.**

- Groq: Free tier (~30 req/min)
- DuckDuckGo: Unlimited free
- HuggingFace embeddings: Local, free
- Pinecone: Free tier index
- Langfuse: Self-hosted, free
- RAGAS: Open-source, free

---

**Upgraded from prototype to production** — September 2026
