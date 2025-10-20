#!/usr/bin/env python3
"""
Training script for the neural network embedding model.
Uses the current repository's code to train a domain-specific embedding model.
"""

import os
import sys
import asyncio
import pathlib
from typing import List, Dict, Any
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import json

# Add parent directory to path for imports
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from services.simple_nn_client import SimpleNNEmbeddingClient
from parser.extract_code import parse_repository


class EmbeddingTrainer:
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.model = SimpleNNEmbeddingClient(embedding_dim=embedding_dim)
        self.training_data = []
        self.validation_data = []

    async def collect_training_data(self, repo_urls: List[str]) -> None:
        """Collect code chunks from multiple repositories for training"""
        print(f"Collecting training data from {len(repo_urls)} repositories...")
        
        all_chunks = []
        for repo_url in repo_urls:
            try:
                print(f"Processing {repo_url}...")
                chunks = await parse_repository(repo_url, force_reparse=True)
                all_chunks.extend(chunks)
                print(f"  Found {len(chunks)} chunks")
            except Exception as e:
                print(f"  Error processing {repo_url}: {e}")
        
        print(f"Total chunks collected: {len(all_chunks)}")
        
        # Split into training and validation
        if len(all_chunks) > 10:
            train_chunks, val_chunks = train_test_split(
                all_chunks, test_size=0.2, random_state=42
            )
        else:
            train_chunks = all_chunks
            val_chunks = all_chunks[:2] if len(all_chunks) > 2 else all_chunks
        
        self.training_data = train_chunks
        self.validation_data = val_chunks
        
        print(f"Training chunks: {len(self.training_data)}")
        print(f"Validation chunks: {len(self.validation_data)}")

    def prepare_training_data(self) -> tuple:
        """Prepare training data for the neural network"""
        print("Preparing training data...")
        
        # Extract texts and create features
        train_texts = [chunk["content"] for chunk in self.training_data]
        val_texts = [chunk["content"] for chunk in self.validation_data]
        
        # Get TF-IDF features for training
        train_features = self.model._create_training_data(train_texts)
        val_features = self.model._create_training_data(val_texts)
        
        # Create target embeddings (we'll use TF-IDF as targets for simplicity)
        # In a real scenario, you'd have better target embeddings
        train_targets = train_features
        val_targets = val_features
        
        return (train_features, train_targets), (val_features, val_targets)

    def train_model(self) -> Dict[str, float]:
        """Train the neural network model"""
        print("Training neural network model...")
        
        # Prepare data
        (X_train, y_train), (X_val, y_val) = self.prepare_training_data()
        
        # Scale features
        X_train_scaled = self.model.scaler.fit_transform(X_train)
        X_val_scaled = self.model.scaler.transform(X_val)
        
        # Train the model
        print("Fitting neural network...")
        self.model.nn_model.fit(X_train_scaled, y_train)
        self.model.nn_model_fitted = True
        
        # Evaluate
        train_pred = self.model.nn_model.predict(X_train_scaled)
        val_pred = self.model.nn_model.predict(X_val_scaled)
        
        train_mse = mean_squared_error(y_train, train_pred)
        val_mse = mean_squared_error(y_val, val_pred)
        
        metrics = {
            "train_mse": float(train_mse),
            "val_mse": float(val_mse),
            "embedding_dim": self.embedding_dim,
            "train_samples": len(X_train),
            "val_samples": len(X_val)
        }
        
        print(f"Training MSE: {train_mse:.4f}")
        print(f"Validation MSE: {val_mse:.4f}")
        
        return metrics

    def save_model(self, model_path: str) -> None:
        """Save the trained model"""
        print(f"Saving model to {model_path}...")
        self.model.save_model(model_path)
        
        # Also save training metadata
        metadata = {
            "embedding_dim": self.embedding_dim,
            "training_samples": len(self.training_data),
            "validation_samples": len(self.validation_data),
            "model_type": "simple_nn_embedding"
        }
        
        metadata_path = model_path.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {model_path}")
        print(f"Metadata saved to {metadata_path}")

    def test_embeddings(self, test_texts: List[str]) -> List[List[float]]:
        """Test the trained model on new texts"""
        print("Testing embeddings generation...")
        embeddings = self.model.embed_texts(test_texts)
        print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0]) if embeddings else 0}")
        return embeddings


async def main():
    """Main training function"""
    print("=== Neural Network Embedding Training ===")
    
    # Configuration
    embedding_dim = int(os.getenv("NN_EMBEDDING_DIM", "128"))
    model_path = os.getenv("MODEL_PATH", "trained_embedding_model.pkl")
    
    # Training repositories (you can add more)
    training_repos = [
        "https://github.com/microsoft/vscode",  # Large codebase
        "https://github.com/facebook/react",    # Popular frontend
        "https://github.com/torvalds/linux",   # Large C codebase
    ]
    
    # Add current repository if it's a git repo
    try:
        from git import Repo
        repo = Repo(".")
        if not repo.bare:
            current_repo_url = repo.remotes.origin.url
            if current_repo_url not in training_repos:
                training_repos.append(current_repo_url)
                print(f"Added current repository: {current_repo_url}")
    except Exception:
        print("Current directory is not a git repository, skipping...")
    
    # Initialize trainer
    trainer = EmbeddingTrainer(embedding_dim=embedding_dim)
    
    try:
        # Collect training data
        await trainer.collect_training_data(training_repos)
        
        if not trainer.training_data:
            print("No training data collected. Exiting.")
            return
        
        # Train model
        metrics = trainer.train_model()
        
        # Save model
        trainer.save_model(model_path)
        
        # Test embeddings
        test_texts = [
            "def hello_world(): return 'Hello, World!'",
            "class User: def __init__(self, name): self.name = name",
            "import numpy as np; arr = np.array([1, 2, 3])",
            "async def fetch_data(): return await api.get('/data')",
            "const React = require('react'); export default App;"
        ]
        
        embeddings = trainer.test_embeddings(test_texts)
        
        print("\n=== Training Complete ===")
        print(f"Model saved to: {model_path}")
        print(f"Embedding dimension: {embedding_dim}")
        print(f"Training samples: {metrics['train_samples']}")
        print(f"Validation samples: {metrics['val_samples']}")
        print(f"Training MSE: {metrics['train_mse']:.4f}")
        print(f"Validation MSE: {metrics['val_mse']:.4f}")
        
    except Exception as e:
        print(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
