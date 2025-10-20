#!/usr/bin/env python3
"""
Convenience script to run the complete training pipeline.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from train_embeddings import main as train_main


async def run_complete_training():
    """Run the complete training pipeline"""
    print("=== AutoDoc.AI Embedding Training Pipeline ===")
    
    # Set default model path
    model_path = os.getenv("MODEL_PATH", "trained_embedding_model.pkl")
    
    print(f"Training model with path: {model_path}")
    print("This will:")
    print("1. Collect code from multiple repositories")
    print("2. Train a neural network embedding model")
    print("3. Save the trained model")
    print("4. Test the model performance")
    print()
    
    try:
        # Run training
        await train_main()
        
        print("\n=== Training Pipeline Complete ===")
        print(f"Trained model saved to: {model_path}")
        print("\nTo use the trained model:")
        print("1. Set EMBEDDINGS_PROVIDER=nn in your .env file")
        print("2. Set MODEL_PATH to the saved model file")
        print("3. Restart your FastAPI server")
        
    except Exception as e:
        print(f"Training pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_complete_training())
