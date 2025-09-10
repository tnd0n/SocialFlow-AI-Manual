# OpenAI API provider
import os
import requests
from typing import List, Dict, Any
from llm_providers.base import LLMProvider

class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""
    
    def __init__(self):
        super().__init__()
        self.name = "openai"
        self.api_key = None
        self.max_daily_usage = 100
        self.models = ["gpt-3.5-turbo", "gpt-4"]
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request to OpenAI API"""
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")
            
        if not self.api_key:
            raise RuntimeError("OpenAI API key not found in environment")
            
        if not self.check_rate_limits():
            raise RuntimeError("Daily rate limit exceeded")
            
        model = kwargs.get("model", "gpt-3.5-turbo")
        
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
            raise RuntimeError(f"OpenAI API error: {str(e)}")