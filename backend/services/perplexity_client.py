import os
import time
import httpx
from typing import Optional
from .api_config import (
    PERPLEXITY_MODELS,
    PERPLEXITY_API_URL,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    MAX_OUTPUT_TOKENS
)


class PerplexityClient:
    def __init__(self) -> None:
        api_key = os.getenv("PPLX_API_KEY")
        if not api_key:
            raise RuntimeError("PPLX_API_KEY is required for Perplexity API")
        self.api_key = api_key
        
        # Get supported models
        supported_models = ['sonar', 'sonar-pro', 'sonar-deep-research', 'sonar-reasoning', 'sonar-reasoning-pro']
        
        # Override model from env if provided, or use default
        self.model = os.getenv("PPLX_MODEL", PERPLEXITY_MODELS["default"])
        
        # Validate the model
        if self.model not in supported_models:
            raise ValueError(f"Invalid model: {self.model}. Must be one of {supported_models}")

    def generate_markdown(self, system_prompt: str, user_prompt: str) -> str:
        """Generate README markdown using the Perplexity API.
        
        Args:
            system_prompt: The system prompt to guide the model
            user_prompt: The user prompt containing repository context
            
        Returns:
            str: The generated README markdown
            
        Raises:
            RuntimeError: If the API call fails or no content is received
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Truncate prompts if they're too long
        max_prompt_length = 32000
        if len(user_prompt) > max_prompt_length:
            print(f"Truncating user prompt from {len(user_prompt)} to {max_prompt_length} characters")
            user_prompt = user_prompt[:max_prompt_length] + "..."

        # Format messages according to Perplexity API requirements
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,  # Lower temperature for more focused output
            "max_tokens": 4000   # Ensure we have enough tokens for a full README
        }

        max_retries = 3
        retry_delay = 5  # Initial delay in seconds
        
        for attempt in range(max_retries):
            try:
                # Configure longer timeout for generation
                timeout = httpx.Timeout(
                    connect=30.0,     # Connection timeout
                    read=600.0,       # Read timeout (10 minutes)
                    write=30.0,       # Write timeout
                    pool=30.0         # Pool timeout
                )
                
                with httpx.Client(timeout=timeout) as client:
                    print(f"\nAttempt {attempt + 1}/{max_retries}")
                    print(f"Making request to Perplexity API...")
                    print(f"URL: {PERPLEXITY_API_URL}")
                    print(f"Model: {self.model}")
                    print(f"System prompt length: {len(system_prompt)}")
                    print(f"User prompt length: {len(user_prompt)}")
                    print("Sending request...")
                    
                    resp = client.post(PERPLEXITY_API_URL, headers=headers, json=payload)
                    print(f"Received response with status: {resp.status_code}")
                    
                    if resp.status_code != 200:
                        error_text = resp.text
                        print(f"Error response: {error_text}")
                        try:
                            error_json = resp.json()
                            if 'error' in error_json:
                                error_text = str(error_json['error'])
                        except Exception:
                            pass
                        raise RuntimeError(f"Perplexity API error: {error_text}")
                    
                    print("Parsing response...")
                    data = resp.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    
                    if not content:
                        raise RuntimeError("No content received from Perplexity API")
                    
                    print(f"Successfully generated README with {len(content)} characters")
                    return content
                    
            except httpx.TimeoutException as e:
                print(f"\nTimeout on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Failed after {max_retries} attempts: {str(e)}")
                    
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {str(e)}")
                raise
        
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                # Increase timeout for longer generations
                timeout = httpx.Timeout(
                    connect=30.0,     # Connection timeout
                    read=600.0,       # Read timeout (10 minutes)
                    write=30.0,       # Write timeout
                    pool=30.0         # Pool timeout
                )
                
                with httpx.Client(timeout=timeout) as client:
                    print(f"\nAttempt {attempt + 1}/{max_retries}")
                    print(f"Making request to Perplexity API...")
                    print(f"URL: {PERPLEXITY_API_URL}")
                    print(f"Model: {self.model}")
                    print(f"System prompt length: {len(system_prompt)}")
                    print(f"User prompt length: {len(user_prompt)}")
                    print("Sending request...")
                    
                    resp = client.post(PERPLEXITY_API_URL, headers=headers, json=payload)
                    print(f"Received response with status: {resp.status_code}")
                    
                    if resp.status_code != 200:
                        error_text = resp.text
                        print(f"Error response: {error_text}")
                        try:
                            error_json = resp.json()
                            if 'error' in error_json:
                                error_text = str(error_json['error'])
                        except Exception:
                            pass
                        raise RuntimeError(f"Perplexity API error: {error_text}")
                    
                    print("Parsing response...")
                    data = resp.json()
                    content = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    
                    if not content:
                        raise RuntimeError("No content received from Perplexity API")
                    
                    print(f"Successfully generated README with {len(content)} characters")
                    return content
                    
            except httpx.TimeoutException as e:
                print(f"\nTimeout on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Failed after {max_retries} attempts: {str(e)}")
            except Exception as e:
                print(f"\nError on attempt {attempt + 1}: {str(e)}")
                raise
