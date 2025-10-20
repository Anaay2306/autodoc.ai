from typing import List, Dict, Any
import os
from .supabase_client import SupabaseClient


class EmbeddingStore:
    def __init__(self) -> None:
        provider = os.getenv("EMBEDDINGS_PROVIDER", "hf").lower()
        # provider: 'hf' (huggingface inference/local), 'openai', 'cohere', 'nn', 'tfidf'
        if provider == "cohere":
            try:
                from .cohere_client import CohereClient  # type: ignore

                self.embedder = CohereClient()
            except Exception as e:
                raise RuntimeError(
                    "Cohere provider selected but cohere client is unavailable. Install 'cohere' or switch EMBEDDINGS_PROVIDER."
                ) from e
        elif provider == "openai":
            try:
                from .openai_client import OpenAIClient  # type: ignore

                self.embedder = OpenAIClient()
            except Exception as e:
                raise RuntimeError("OPENAI_API_KEY is required for OpenAI provider") from e
        elif provider in {"hf", "huggingface"}:
            # Prefer HF inference client if available, else try local sentence-transformers
            try:
                from .hf_client import HuggingFaceEmbeddingClient  # type: ignore

                self.embedder = HuggingFaceEmbeddingClient()
            except Exception:
                # Fallback to OpenAI if HF not configured or local packages missing
                try:
                    from .openai_client import OpenAIClient  # type: ignore

                    self.embedder = OpenAIClient()
                except Exception as e:
                    raise RuntimeError(
                        "Hugging Face client unavailable and OPENAI_API_KEY not set. Configure HF or OpenAI."
                    ) from e
        elif provider == "nn":
            try:
                from .simple_nn_client import SimpleNNEmbeddingClient  # type: ignore

                embedding_dim = int(os.getenv("NN_EMBEDDING_DIM", "128"))
                self.embedder = SimpleNNEmbeddingClient(embedding_dim=embedding_dim)
            except Exception as e:
                raise RuntimeError("NN provider selected but required client is unavailable.") from e
        elif provider == "tfidf":
            try:
                from .tfidf_client import TFIDFEmbeddingClient  # type: ignore

                self.embedder = TFIDFEmbeddingClient()
            except Exception as e:
                raise RuntimeError("TF-IDF provider selected but required client is unavailable.") from e
        else:
            # default: try HF then OpenAI
            try:
                from .hf_client import HuggingFaceEmbeddingClient  # type: ignore

                self.embedder = HuggingFaceEmbeddingClient()
            except Exception:
                try:
                    from .openai_client import OpenAIClient  # type: ignore

                    self.embedder = OpenAIClient()
                except Exception as e:
                    raise RuntimeError("No embedding provider is available. Configure HF or OpenAI.") from e

        self.supabase = SupabaseClient()

    async def index_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        texts = [c["content"] for c in chunks]
        vectors = self.embedder.embed_texts(texts)
        rows = []
        for chunk, vec in zip(chunks, vectors):
            rows.append(
                {
                    "repo_url": chunk["repo_url"],
                    "file_path": chunk["file_path"],
                    "content": chunk["content"],
                    "metadata": chunk.get("metadata", {}),
                    "embedding": vec,
                }
            )
        self.supabase.insert_code_chunks(rows)

    async def search_chunks(self, repo_url: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        q_vec = self.embedder.embed_texts([query])[0]
        candidates = self.supabase.search_code_chunks(repo_url, q_vec, top_k=200)
        if not candidates:
            return []
        return candidates[:top_k]
