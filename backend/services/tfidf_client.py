import os
import pickle
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

TFIDF_MAX_FEATURES = 1536  # Fixed size to match database schema
TFIDF_NGRAM_RANGE = (1, 2)  # unigrams and bigrams


class TFIDFEmbeddingClient:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            stop_words='english',
            lowercase=True,
            strip_accents='unicode'
        )
        self.fitted = False
        self.corpus_texts = []

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        # Add to corpus for fitting
        self.corpus_texts.extend(texts)
        
        # Fit vectorizer on all seen texts
        if not self.fitted:
            self.vectorizer.fit(self.corpus_texts)
            self.fitted = True
        
        # Transform texts to TF-IDF vectors
        tfidf_matrix = self.vectorizer.transform(texts)
        
        # Convert to dense format and normalize
        vectors = tfidf_matrix.toarray()
        # L2 normalize for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / (norms + 1e-8)  # avoid division by zero
        
        return vectors.tolist()

    def save_model(self, path: str) -> None:
        """Save the fitted vectorizer for reuse"""
        with open(path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'fitted': self.fitted,
                'corpus_texts': self.corpus_texts
            }, f)

    def load_model(self, path: str) -> None:
        """Load a previously fitted vectorizer"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.fitted = data['fitted']
            self.corpus_texts = data['corpus_texts']
