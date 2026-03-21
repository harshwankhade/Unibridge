# UniBridge

A platform that connects industry with university IP and research through AI-powered semantic search.

---

## Services

| Service | Port | Responsibility |
|---|---|---|
| **gateway** | 8000 | API Gateway — JWT verification and role-based routing |
| **auth** | 8001 | Authentication — register, login, user management |
| **search** | 8002 | Search — RAG pipeline, query translation, re-ranking |
| **data** | 8003 | Data — ChromaDB vector store, patent ingestion |
| **submission** | 8004 | Submission — IP submission and approval workflow |
| **analytics** | 8005 | Analytics — search event logging, trends, domain gaps |
| **admin** | 8006 | Admin — BFF aggregator for the admin portal |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, Vite, TailwindCSS, Recharts |
| **Backend** | FastAPI (Python) |
| **Vector Database** | ChromaDB |
| **AI Pipeline** | LangChain, sentence-transformers, Anthropic API |
| **Infrastructure** | Docker, Docker Compose |

---

## Getting Started

Coming soon.
