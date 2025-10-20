# AutoDoc.AI

AutoDoc.AI is an intelligent GitHub repository documentation generator. It analyzes a public GitHub repository, semantically indexes the codebase, and uses an LLM to produce a high-quality README.md with sections like Overview, Installation, Usage, API, and more.

## Tech Stack
- Frontend: Next.js 14 + TypeScript + TailwindCSS + ShadCN UI
- Backend: FastAPI (Python) + Perplexity (generation) + OpenAI Embeddings + tree-sitter
- Database: Supabase (PostgreSQL + Auth + pgvector)
- Deploy: Vercel (frontend) + Supabase (db) + any Python host for FastAPI
- CI/CD: GitHub Actions to auto-regenerate README on push

## Features
- Paste a GitHub repo URL and generate a README.md
- Code parsing via tree-sitter to extract functions, classes, and docstrings
- Chunking + metadata, vector embeddings via OpenAI
- Semantic retrieval to build a high-signal context for the LLM
- Minimalist UI with markdown preview, copy, and download

## Monorepo Structure
```
autodoc-ai/
├── frontend/               # Next.js app (Vercel deploy)
├── backend/                # FastAPI app (parsing + LLM)
├── supabase/               # SQL schema (pgvector + tables)
├── .github/workflows/      # CI for README generation
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Environment Variables
Copy `.env.example` to `.env` files in respective apps and fill in values.

Required variables:
- OPENAI_API_KEY (embeddings)
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SUPABASE_SERVICE_KEY (server-side only, for backend inserts/vector search)
- PPLX_API_KEY (Perplexity generation)
- NEXT_PUBLIC_BACKEND_URL (frontend → backend)

Optional:
- PPLX_MODEL (default: `llama-3.1-sonar-large-128k-online`)
- PPLX_API_URL (default: `https://api.perplexity.ai/chat/completions`)

## Backend (FastAPI)
### Run locally
```bash
# from autodoc-ai/backend
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Key endpoints
- POST /parse_repo { repo_url }
- POST /generate_readme { repo_url, top_k? }
- POST /search_chunks { repo_url, query, top_k? }

## Frontend (Next.js)
### Run locally
```bash
# from autodoc-ai/frontend
npm install
npm run dev
```
Set `NEXT_PUBLIC_BACKEND_URL` to the FastAPI URL (e.g., `http://localhost:8000`).

## Supabase
- Create a new Supabase project
- Execute `supabase/schema.sql` against your database
- Ensure `pgvector` is enabled (installed by default in Supabase)

## GitHub Action
`.github/workflows/generate-doc.yml` triggers on push and runs the backend script to regenerate README, committing it back to the repository under `.autodoc/README.md` or root if desired.

## High-level Flow
1. User submits repo URL
2. Backend clones repo to a temp folder
3. Parse code using tree-sitter into structured chunks
4. Generate embeddings per chunk and store in Supabase
5. Retrieve top-N chunks and synthesize README with Perplexity
6. Return Markdown to the frontend for preview/download

## Prompting Strategy
System prompt:
"You are an expert documentation writer. Given this repository analysis (function signatures, docstrings, comments, examples), generate a professional README.md including Overview, Features, Architecture, Installation, Usage, API, Examples, Contributing, and License."

## Notes
- Multi-language parsing via `tree_sitter_languages` with fallback to whole-file chunking.
- Ensure you comply with repository licenses when generating and committing documentation.

## License
MIT
