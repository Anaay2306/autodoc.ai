import os
from typing import List
import cohere

COHERE_MODEL = os.getenv("COHERE_EMBED_MODEL", "embed-multilingual-v3.0")


class CohereClient:
    def __init__(self) -> None:
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise RuntimeError("COHERE_API_KEY is required for embeddings")
        self.client = cohere.Client(api_key)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embed(texts=texts, model=COHERE_MODEL, input_type="search_document")
        return [list(map(float, v)) for v in resp.embeddings]
