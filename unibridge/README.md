# UniBridge

A B2B platform that connects industry companies with university intellectual property — patents and research papers — from QS-ranked global institutions, powered by AI semantic search.

---

## What It Does

- Industry users search for relevant university research using plain business language
- AI translates business queries into academic terminology and retrieves the most relevant results
- University users submit patents and research papers for indexing
- Admins review submissions, manage users, and monitor platform analytics

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLite + SQLAlchemy |
| Frontend | React + Vite + TailwindCSS |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Reranking | cross-encoder (ms-marco-MiniLM-L-6-v2) |
| LLM | OpenAI GPT-3.5-turbo |
| Containerization | Docker + Docker Compose |

---

## Architecture

7 microservices behind an API Gateway:

| Service | Port | Responsibility |
|---|---|---|
| gateway | 8000 | Single entry point, JWT verification, request routing |
| auth | 8001 | User registration, login, JWT tokens |
| search | 8002 | AI search pipeline (translate → retrieve → rerank → explain) |
| data | 8003 | ChromaDB vector store, embeddings, TRL prediction |
| submission | 8004 | IP submission lifecycle (submit → approve → index) |
| analytics | 8005 | Search event logging, trending, gaps |
| admin | 8006 | Admin proxy for users, submissions, analytics |

---

## Prerequisites

- Docker Desktop installed and running
- Node.js and npm installed
- OpenAI API key

---

## Running the Project

### Step 1 — Set up environment variables

Create a `.env` file in the project root:

```
JWT_SECRET=your_secret_key_here
OPENAI_API_KEY=your_openai_key_here

GATEWAY_PORT=8000
AUTH_PORT=8001
SEARCH_PORT=8002
DATA_PORT=8003
SUBMISSION_PORT=8004
ANALYTICS_PORT=8005
ADMIN_PORT=8006

AUTH_URL=http://auth:8001
SEARCH_URL=http://search:8002
DATA_URL=http://data:8003
SUBMISSION_URL=http://submission:8004
ANALYTICS_URL=http://analytics:8005
ADMIN_URL=http://admin:8006
GATEWAY_URL=http://gateway:8000
```

### Step 2 — Build and start all services

```bash
docker compose build
docker compose up
```

Wait until all 7 containers are healthy. This takes about 60–90 seconds on first run as the embedding model downloads.

### Step 3 — Seed demo users

Open a new terminal while containers are running:

```bash
docker exec unibridge-auth python3 seed.py
```

### Step 4 — Run data ingestion

```bash
docker exec unibridge-data python3 ingest.py
```

This embeds all records into ChromaDB. Takes a few minutes depending on dataset size.

### Step 5 — Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## Demo Accounts

| Email | Password | Role |
|---|---|---|
| industry@demo.com | demo1234 | Industry |
| university@demo.com | demo1234 | University |
| admin@demo.com | demo1234 | Admin |

---

## Search Modes

| Mode | Use Case |
|---|---|
| Solve a Problem | Find research that addresses a specific technical challenge |
| Benchmark Technologies | Compare approaches and technologies in a domain |
| Landscape a Field | Explore the full research landscape of a field |

---

## Useful Docker Commands

```bash
# Check container status
docker compose ps

# View logs for a specific service
docker logs unibridge-data
docker logs unibridge-auth
docker logs unibridge-gateway

# Restart a single service
docker compose restart search

# Stop everything
docker compose down

# Stop and wipe all data (fresh start)
docker compose down -v
```

---

## Data Sources

- **Patents** — Lens.org API
- **Research Papers** — Semantic Scholar API
- **Universities** — QS World University Rankings (top 100)