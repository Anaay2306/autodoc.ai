import os
from typing import List

HF_DEFAULT_MODEL = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
HF_USE_INFERENCE = os.getenv("HF_USE_INFERENCE", "false").lower() in {"1", "true", "yes"}


class HuggingFaceEmbeddingClient:
    def __init__(self) -> None:
        self.model_name = HF_DEFAULT_MODEL
        if HF_USE_INFERENCE:
            from huggingface_hub import InferenceClient  # lazy import
            token = os.getenv("HF_TOKEN")
            if not token:
                raise RuntimeError("HF_TOKEN is required when HF_USE_INFERENCE=true")
            # Uses hosted Inference API, feature-extraction task
            self.client = InferenceClient(api_key=token)
            self.mode = "inference"
        else:
            from sentence_transformers import SentenceTransformer  # lazy import
            self.model = SentenceTransformer(self.model_name)
            self.mode = "local"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self.mode == "local":
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return embeddings.tolist()
        # Inference API: use feature-extraction
        # The client returns list[list[float]] per input when using feature_extraction
        features: List[List[float]] = []
        for t in texts:
            vec = self.client.feature_extraction(t, model=self.model_name)
            # Some models return nested structure (sequence). If nested, average pool.
            if isinstance(vec, list) and vec and isinstance(vec[0], list):
                # simple mean pooling across tokens
                dim = len(vec[0])
                pooled = [0.0] * dim
                for tok in vec:
                    for i, v in enumerate(tok):
                        pooled[i] += float(v)
                pooled = [v / max(1, len(vec)) for v in pooled]
                features.append(pooled)
            else:
                features.append([float(v) for v in vec])
        return features
