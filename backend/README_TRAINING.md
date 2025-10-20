# Training Neural Network Embeddings

This guide explains how to train your own neural network embedding model for AutoDoc.AI.

## Overview

The neural network embedding model learns to create dense vector representations of code by training on actual repository code. This makes it domain-specific and potentially more effective than generic embeddings.

## Training Process

1. **Data Collection**: Gathers code from multiple repositories
2. **Feature Extraction**: Converts code to TF-IDF features
3. **Neural Network Training**: Trains an MLP to learn dense embeddings
4. **Model Saving**: Saves the trained model for use in the main application

## Quick Start

### 1. Train the Model

```bash
cd autodoc-ai/backend
python scripts/run_training.py
```

This will:
- Collect code from popular repositories (VS Code, React, Linux)
- Train a neural network embedding model
- Save the model to `trained_embedding_model.pkl`

### 2. Use the Trained Model

Set in your `.env` file:
```ini
EMBEDDINGS_PROVIDER=nn
MODEL_PATH=trained_embedding_model.pkl
NN_EMBEDDING_DIM=128
```

### 3. Test the Model

```bash
python scripts/load_trained_model.py
```

## Advanced Configuration

### Custom Training Repositories

Edit `scripts/train_embeddings.py` and modify the `training_repos` list:

```python
training_repos = [
    "https://github.com/your-org/your-repo",
    "https://github.com/another/repo",
    # Add more repositories
]
```

### Custom Model Parameters

Set environment variables:

```bash
export NN_EMBEDDING_DIM=256  # Larger embedding dimension
export MODEL_PATH=my_custom_model.pkl  # Custom model path
```

### Training on Your Own Code

The script automatically includes your current repository if it's a git repo. To train on specific repositories:

```bash
# Train on specific repos
python scripts/train_embeddings.py
```

## Model Architecture

The neural network uses:
- **Input**: TF-IDF features (1000 dimensions)
- **Hidden Layers**: 256 → 128 → embedding_dim
- **Activation**: ReLU
- **Optimizer**: Adam
- **Output**: Dense embeddings (normalized)

## Training Metrics

The training process reports:
- **Training MSE**: Mean squared error on training data
- **Validation MSE**: Mean squared error on validation data
- **Sample Counts**: Number of training/validation samples

## Model Files

After training, you'll have:
- `trained_embedding_model.pkl`: The trained model
- `trained_embedding_model_metadata.json`: Training metadata

## Integration with Main App

Once trained, the model integrates seamlessly:

1. Set `EMBEDDINGS_PROVIDER=nn` in your `.env`
2. Ensure `MODEL_PATH` points to your trained model
3. Restart the FastAPI server
4. The embedding store will automatically use your trained model

## Performance Tips

- **More Data**: Train on more repositories for better performance
- **Larger Models**: Increase `NN_EMBEDDING_DIM` for more capacity
- **Domain-Specific**: Train on repositories similar to your target domain
- **Regular Retraining**: Retrain periodically with new data

## Troubleshooting

### Out of Memory
- Reduce `NN_EMBEDDING_DIM`
- Use fewer training repositories
- Process repositories in smaller batches

### Poor Performance
- Train on more diverse repositories
- Increase embedding dimension
- Check that training data is representative

### Model Loading Issues
- Ensure model file exists and is readable
- Check that all dependencies are installed
- Verify the model was trained successfully

## Example Training Output

```
=== Neural Network Embedding Training ===
Collecting training data from 3 repositories...
Processing https://github.com/microsoft/vscode...
  Found 1250 chunks
Processing https://github.com/facebook/react...
  Found 890 chunks
Processing https://github.com/torvalds/linux...
  Found 2100 chunks
Total chunks collected: 4240
Training chunks: 3392
Validation chunks: 848
Preparing training data...
Training neural network model...
Fitting neural network...
Training MSE: 0.0234
Validation MSE: 0.0287
Saving model to trained_embedding_model.pkl...
Model saved to trained_embedding_model.pkl
Metadata saved to trained_embedding_model_metadata.json

=== Training Complete ===
Model saved to: trained_embedding_model.pkl
Embedding dimension: 128
Training samples: 3392
Validation samples: 848
Training MSE: 0.0234
Validation MSE: 0.0287
```
