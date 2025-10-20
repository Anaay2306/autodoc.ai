import os
from typing import List
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


class OpenAIClient:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=api_key)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # Batches are small for simplicity
        response = self.client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        return [item.embedding for item in response.data]

    def generate_markdown(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""
