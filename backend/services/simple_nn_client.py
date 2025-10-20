import os
import pickle
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
import re

class SimpleNNEmbeddingClient:
    """
    A simple neural network embedding model trained from scratch.
    Uses TF-IDF features as input and learns dense embeddings.
    """
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        self.scaler = StandardScaler()
        self.nn_model = MLPRegressor(
            hidden_layer_sizes=(256, 128, embedding_dim),
            activation='relu',
            solver='adam',
            max_iter=100,
            random_state=42
        )
        self.fitted = False
        self.corpus_texts = []

    def _preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        # Remove code blocks and keep only text
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]+`', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _create_training_data(self, texts: List[str]) -> np.ndarray:
        """Create training data from texts"""
        processed_texts = [self._preprocess_text(t) for t in texts]
        self.corpus_texts.extend(processed_texts)
        
        if not self.fitted:
            # Fit vectorizer on all texts
            self.vectorizer.fit(self.corpus_texts)
            self.fitted = True
        
        # Transform to TF-IDF features
        tfidf_matrix = self.vectorizer.transform(processed_texts)
        return tfidf_matrix.toarray()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        if not texts:
            return []
        
        # Create training data
        X = self._create_training_data(texts)
        
        if not hasattr(self, 'nn_model_fitted') or not self.nn_model_fitted:
            # Train the neural network
            # For simplicity, we'll use the TF-IDF features as both input and target
            # In a real scenario, you'd have better training data
            X_scaled = self.scaler.fit_transform(X)
            
            # Train the model to learn embeddings
            # We'll use a simple approach: learn to compress TF-IDF to dense vectors
            self.nn_model.fit(X_scaled, X_scaled)
            self.nn_model_fitted = True
        
        # Generate embeddings
        X_scaled = self.scaler.transform(X)
        embeddings = self.nn_model.predict(X_scaled)
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / (norms + 1e-8)
        
        return embeddings.tolist()

    def save_model(self, path: str) -> None:
        """Save the trained model"""
        with open(path, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'scaler': self.scaler,
                'nn_model': self.nn_model,
                'fitted': self.fitted,
                'nn_model_fitted': getattr(self, 'nn_model_fitted', False),
                'corpus_texts': self.corpus_texts,
                'embedding_dim': self.embedding_dim
            }, f)

    def load_model(self, path: str) -> None:
        """Load a previously trained model"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.scaler = data['scaler']
            self.nn_model = data['nn_model']
            self.fitted = data['fitted']
            self.nn_model_fitted = data.get('nn_model_fitted', False)
            self.corpus_texts = data['corpus_texts']
            self.embedding_dim = data.get('embedding_dim', 128)
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            'embedding_dim': self.embedding_dim,
            'fitted': self.fitted,
            'nn_model_fitted': getattr(self, 'nn_model_fitted', False),
            'corpus_size': len(self.corpus_texts),
            'vectorizer_features': self.vectorizer.get_feature_names_out().shape[0] if self.fitted else 0
        }
