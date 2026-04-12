# UniBridge — Project Context for AI Agent

## What is UniBridge?
A B2B platform that connects industry companies with university intellectual property (patents and research papers) from QS-ranked global institutions. Core feature is AI-powered semantic search over real academic data.

---

## Architecture — 7 Microservices

| Service | Port | Description |
|---|---|---|
| gateway | 8000 | API Gateway (not built yet — Phase 7) |
| auth | 8001 | JWT auth, user management |
| search | 8002 | Full AI search pipeline |
| data | 8003 | ChromaDB vector store, embeddings |
| submission | 8004 | IP submission lifecycle |
| analytics | 8005 | Search event logging and stats |
| admin | 8006 | Admin proxy service |

## 3 Portals
- **Industry Portal** — semantic search, bookmarks
- **University Portal** — submit IP, track submissions
- **Admin Portal** — approve/reject submissions, manage users, view analytics

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLite + SQLAlchemy |
| Frontend | React + Vite + TailwindCSS |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` |
| Reranking | cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | OpenAI GPT-3.5-turbo |
| Containerization | Docker + docker-compose |

---

## AI Search Pipeline
1. **Query Translation** — rewrites business language into academic/patent terminology using GPT-3.5-turbo. Category-aware: Solve / Benchmark / Landscape modes.
2. **Stage 1 Retrieval** — vector search top 50 from ChromaDB via Data Service
3. **Stage 2 Reranking** — cross-encoder reranks to top 10
4. **Explainer** — GPT-3.5-turbo generates one-line relevance explanation per result

---

## TRL Classifier (in `services/data/trl_classifier.py`)
- **Rule-based**: weighted keyword matching per TRL tier 1–9, returns TRL + confidence + matched keywords
- **LLM-based**: GPT-3.5-turbo fallback, returns TRL + confidence + reasoning
- **Hybrid master function**: `predict_trl(abstract, date_published, legal_status)`
  - Uses rules if confidence > 0.7, else falls back to LLM
  - Secondary adjustments: patent age + legal_status (ACTIVE + age > 5 → TRL+1, age < 2 → TRL-1)
- **`batch_evaluate(samples)`**: compares all 3 approaches side by side on 20 records

---

## Dataset
- **Patents**: Lens.org API (switched from PatentsView which is down)
- **Papers**: Semantic Scholar API
- **~1,541 records** total
- Saved as `data/processed_records.json` after cleaning
- Indian universities (IITs, IISc, NITs etc.) flagged with `is_indian: True`

---

## Folder Structure
```
unibridge/
├── services/
│   ├── gateway/
│   ├── auth/
│   ├── search/
│   │   ├── query_translator.py
│   │   ├── retriever.py
│   │   ├── explainer.py
│   │   └── main.py
│   ├── data/
│   │   ├── trl_classifier.py
│   │   ├── ingest.py
│   │   └── main.py
│   ├── submission/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── main.py
│   ├── analytics/
│   └── admin/
├── frontend/
│   └── src/
│       ├── api/client.js
│       ├── utils/auth.js
│       ├── utils/parseJWT.js
│       ├── components/
│       │   ├── ProtectedRoute.jsx
│       │   ├── RoleRoute.jsx
│       │   └── TechCard.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Register.jsx
│           ├── industry/
│           │   ├── Dashboard.jsx
│           │   ├── Search.jsx
│           │   └── Bookmarks.jsx
│           └── university/
│               ├── Dashboard.jsx
│               ├── SubmitIP.jsx
│               └── Submissions.jsx
└── data/
    ├── universities.py
    ├── scrape_patents.py
    ├── scrape_papers.py
    ├── process_data.py
    ├── raw_patents.json
    ├── raw_papers.json
    └── processed_records.json
```

---

## Environment Variables (.env)
```
JWT_SECRET=...
LENS_API_TOKEN=...
OPENAI_API_KEY=...
GATEWAY_PORT=8000
AUTH_PORT=8001
SEARCH_PORT=8002
DATA_PORT=8003
SUBMISSION_PORT=8004
ANALYTICS_PORT=8005
ADMIN_PORT=8006
GATEWAY_URL=http://gateway:8000
AUTH_URL=http://auth:8001
SEARCH_URL=http://search:8002
DATA_URL=http://data:8003
SUBMISSION_URL=http://submission:8004
ANALYTICS_URL=http://analytics:8005
ADMIN_URL=http://admin:8006
```

---

## Demo Users (seeded via `services/auth/seed.py`)
| Email | Password | Role |
|---|---|---|
| industry@demo.com | demo1234 | industry |
| university@demo.com | demo1234 | university |
| admin@demo.com | demo1234 | admin |

---

## Current Progress

### Completed
- ✅ Phase 0 — Monorepo structure, .gitignore, README, requirements.txt, main.py health endpoints, Dockerfiles
- ✅ Phase 1 — universities.py, scrape_patents.py, scrape_papers.py, process_data.py, trl_classifier.py (rule + LLM + hybrid), ingest.py, data service main.py
- ✅ Phase 2 — Auth service (database.py, models.py, main.py, seed.py), React frontend scaffold, Login.jsx, Register.jsx, App.jsx with full routing, ProtectedRoute, RoleRoute, api/client.js, utils/auth.js, utils/parseJWT.js
- ✅ Phase 3 — query_translator.py, retriever.py, explainer.py, search main.py, Industry Portal (Dashboard, Search, TechCard, Bookmarks)
- ✅ Phase 4.1 — Submission service (database.py, models.py, main.py)
- ✅ Phase 4.2 — University Portal (Dashboard, SubmitIP, Submissions)

### Remaining
- ⬜ Phase 5 — Analytics Service
- ⬜ Phase 6 — Admin Service + Admin Portal
- ⬜ Phase 7 — API Gateway
- ⬜ Phase 8 — Integration & Testing
- ⬜ Phase 9 — Architecture Documentation
- ⬜ Phase 10 — Polish & Demo

---

## Important Known Issues & Decisions

### Temporary (revert in Phase 7)
- `src/api/client.js` baseURL is currently `http://localhost:8001` (pointing directly at Auth Service)
- Search.jsx calls `http://localhost:8002/search` directly
- Submission calls go to `http://localhost:8004` directly
- All of these revert to `http://localhost:8000` (Gateway) in Phase 7
- Login.jsx uses `/login` not `/auth/login` (reverts to `/auth/login` in Phase 7)
- Register.jsx uses `/register` not `/auth/register` (same)

### CORS
- All FastAPI services need CORSMiddleware allowing `http://localhost:5173`
- Must be added to every service's main.py immediately after `app = FastAPI()`

### Docker
- Data service needs `start_period: 60s` (sentence-transformers loads slowly)
- All services need `OPENAI_API_KEY` in environment if they use trl_classifier
- Port numbers in Dockerfiles must be hardcoded, not variables
- ChromaDB volume must match path used in code: `/app/chroma_db`

---

## Prompting Rules (for this project)
1. Prompts are generated for a VS Code + GitHub Copilot AI agent (student free tier)
2. Each prompt is specific to one task — no extras added without permission
3. Every prompt includes: what it does / external tools needed / how to verify
4. Ask for clarification if anything is ambiguous
5. CORS must be included in every service-level prompt by default
6. OpenAI GPT-3.5-turbo is the LLM (not Gemini — switched mid-project)

---

## Design System (Frontend)
- Background: dark navy/slate
- Text: white
- Accent: teal/cyan
- Body font: DM Sans
- Heading font: DM Serif Display
- Google Fonts link must be in `index.html`
