# Perplexity API provider
import os
import requests
from typing import List, Dict, Any
from llm_providers.base import LLMProvider

class PerplexityProvider(LLMProvider):
    """Perplexity AI API provider"""
    
    def __init__(self):
        super().__init__()
        self.name = "perplexity"
        self.api_key = None
        self.max_daily_usage = 50
        self.models = ["llama-3.1-sonar-small-128k-online", "llama-3.1-sonar-large-128k-online"]
        self.base_url = "https://api.perplexity.ai/chat/completions"
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request to Perplexity API"""
        if not self.api_key:
            self.api_key = os.getenv("PERPLEXITY_API_KEY")
            
        if not self.api_key:
            raise RuntimeError("Perplexity API key not found in environment")
            
        if not self.check_rate_limits():
            raise RuntimeError("Daily rate limit exceeded")
            
        model = kwargs.get("model", "llama-3.1-sonar-small-128k-online")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self.daily_usage += 1
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            raise RuntimeError(f"Perplexity API error: {str(e)}")