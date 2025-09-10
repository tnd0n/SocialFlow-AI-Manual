# Google Gemini API provider
import os
from typing import List, Dict, Any
from llm_providers.base import LLMProvider

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class GeminiProvider(LLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self):
        super().__init__()
        self.name = "gemini"
        self.api_key = None
        self.max_daily_usage = 60
        self.models = ["gemini-1.5-flash", "gemini-1.5-pro"]
        self.client = None
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request to Gemini API"""
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Gemini SDK not installed (google-generativeai)")
            
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            
        if not self.api_key:
            raise RuntimeError("Gemini API key not found in environment")
            
        if not self.check_rate_limits():
            raise RuntimeError("Daily rate limit exceeded")
            
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(kwargs.get("model", "gemini-1.5-flash"))
            
            # Convert messages to Gemini format
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            response = model.generate_content(prompt)
            self.daily_usage += 1
            
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")