import os
from typing import List, Dict, Any
from supabase import create_client, Client


class SupabaseClient:
    def __init__(self) -> None:
        url = os.getenv("SUPABASE_URL")
        anon = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not anon:
            raise RuntimeError("SUPABASE_URL and SUPABASE_[ANON|SERVICE]_KEY are required")
        self.client: Client = create_client(url, anon)

    def insert_code_chunks(self, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        self.client.table("code_chunks").insert(rows).execute()

    def search_code_chunks(self, repo_url: str, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        res = self.client.rpc(
            "match_code_chunks",
            {
                "repo_url_filter": repo_url,
                "query_embedding": embedding,
                "match_threshold": 0.7,
                "match_count": top_k,
            },
        ).execute()
        return res.data or []

    def insert_readme_history(self, repo_url: str, markdown: str) -> None:
        self.client.table("readme_history").insert({"repo_url": repo_url, "generated_readme": markdown}).execute()
