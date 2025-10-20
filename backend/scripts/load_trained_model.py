#!/usr/bin/env python3
"""
Script to load a trained embedding model and use it in the main application.
"""

import os
import sys
import pathlib

# Add parent directory to path for imports
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from services.simple_nn_client import SimpleNNEmbeddingClient


def load_trained_model(model_path: str) -> SimpleNNEmbeddingClient:
    """Load a trained embedding model"""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    model = SimpleNNEmbeddingClient()
    model.load_model(model_path)
    print(f"Loaded trained model from {model_path}")
    return model


def test_loaded_model(model_path: str):
    """Test the loaded model with sample texts"""
    try:
        model = load_trained_model(model_path)
        
        # Test with various code snippets
        test_texts = [
            "def calculate_sum(a, b): return a + b",
            "class Database: def connect(self): pass",
            "import pandas as pd; df = pd.DataFrame()",
            "async def fetch_user(id): return await db.get_user(id)",
            "const express = require('express'); const app = express();"
        ]
        
        print("Testing loaded model...")
        embeddings = model.embed_texts(test_texts)
        
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        
        # Test similarity between similar texts
        if len(embeddings) >= 2:
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            print(f"Cosine similarity between first two texts: {similarity:.4f}")
        
        return model
        
    except Exception as e:
        print(f"Error testing model: {e}")
        raise


if __name__ == "__main__":
    model_path = os.getenv("MODEL_PATH", "trained_embedding_model.pkl")
    test_loaded_model(model_path)
