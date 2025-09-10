# Base LLM provider interface
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMProvider(ABC):
    """Base class for all LLM providers"""

    def __init__(self):
        self.name = "base"
        self.models = []
        self.daily_usage = 0
        self.max_daily_usage = 100

    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Main chat interface - must be implemented by subclasses"""
        pass

    def reset_daily_usage(self):
        """Reset daily usage counter"""
        self.daily_usage = 0

    def check_rate_limits(self) -> bool:
        """Check if within rate limits"""
        return self.daily_usage < self.max_daily_usage
