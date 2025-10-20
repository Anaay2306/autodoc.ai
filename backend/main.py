from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional

from services.embedding_store import EmbeddingStore
from services.supabase_client import SupabaseClient
from services.perplexity_client import PerplexityClient
from parser.extract_code import parse_repository
from generator.generate_readme import generate_readme_markdown

load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="AutoDoc.AI API", version="0.1.0")

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepoRequest(BaseModel):
    repo_url: HttpUrl
    force_reparse: Optional[bool] = False


class SearchRequest(BaseModel):
    repo_url: HttpUrl
    query: str
    top_k: int = 20


class GenerateRequest(BaseModel):
    repo_url: HttpUrl
    top_k: int = 80


_store = None
_supabase_client = None
_perplexity = None


def get_store():
    global _store
    if _store is None:
        _store = EmbeddingStore()
    return _store


def get_supabase():
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


def get_perplexity():
    global _perplexity
    if _perplexity is None:
        _perplexity = PerplexityClient()
    return _perplexity


@app.post("/parse_repo")
async def parse_repo(req: RepoRequest):
    try:
        print(f"Attempting to parse {req.repo_url}")
        chunks = await parse_repository(str(req.repo_url), force_reparse=req.force_reparse)
        if chunks:
            await get_store().index_chunks(chunks)
        print(f"Successfully parsed {len(chunks)} chunks.")
        return {"ok": True, "num_chunks": len(chunks)}
    except Exception as e:
        print(f"Error parsing repository: {e}")  # Log the actual error
        raise HTTPException(status_code=500, detail=f"Failed to parse repository: {e}")


@app.post("/search_chunks")
async def search_chunks(req: SearchRequest):
    try:
        results = await get_store().search_chunks(str(req.repo_url), req.query, top_k=req.top_k)
        return {"ok": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_readme")
async def generate_readme(req: GenerateRequest):
    try:
        print(f"Generating README for {req.repo_url}")
        print("Searching for relevant code chunks...")
        results = await get_store().search_chunks(str(req.repo_url), query="overview architecture setup usage api", top_k=req.top_k)
        if not results:
            print("No code chunks found. Make sure repository was parsed first.")
            raise HTTPException(status_code=400, detail="No code chunks found. Parse repository first.")
        
        print(f"Found {len(results)} relevant chunks, generating README...")
        markdown = await generate_readme_markdown(get_perplexity(), str(req.repo_url), results)
        
        print("Storing README in history...")
        try:
            get_supabase().insert_readme_history(str(req.repo_url), markdown)
        except Exception as e:
            print(f"Non-fatal: Failed to store README history: {e}")
            pass
        
        return {"ok": True, "readme": markdown}
    except Exception as e:
        print(f"Error generating README: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"ok": True, "service": "AutoDoc.AI API"}
