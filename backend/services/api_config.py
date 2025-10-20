"""API configuration constants"""

# Perplexity API configuration
PERPLEXITY_MODELS = {
    "default": "sonar-deep-research",  # Best for generating detailed READMEs
    "small": "sonar",                  # Lightweight model for basic tasks
    "large": "sonar-deep-research",    # Best for complex research tasks
    "reasoning": "sonar-reasoning",    # Fast reasoning tasks
    "expert": "sonar-reasoning-pro"    # Premier reasoning capabilities
}

# API URLs
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Default parameters
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 1.0
MAX_OUTPUT_TOKENS = 4000