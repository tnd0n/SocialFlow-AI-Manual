# Base platform interface for SocialFlow AI
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import asyncio
import random
import logging
from datetime import datetime

class BasePlatform(ABC):
    """Base class for all social media platforms"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"SocialFlow.{name}")
        self.daily_actions = 0
        self.last_action_time = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass

    @abstractmethod 
    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to the platform"""
        pass

    @abstractmethod
    async def engage_with_content(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Engage with existing content (comment, like, etc.)"""
        pass

    async def simulate_human_delay(self, action_type: str = "default"):
        """Add realistic delays between actions"""
        delays = {
            "post": random.randint(300, 1800),      # 5-30 minutes
            "comment": random.randint(60, 600),     # 1-10 minutes  
            "read": random.randint(10, 60),         # 10-60 seconds
            "type": random.randint(2, 8),           # 2-8 seconds
            "default": random.randint(30, 120)      # 30s-2min
        }

        delay = delays.get(action_type, delays["default"])
        self.logger.info(f"Simulating human delay: {delay}s for {action_type}")
        await asyncio.sleep(delay)

    def log_action(self, action: str, result: Dict[str, Any]):
        """Log platform action with timestamp"""
        log_entry = {
            "platform": self.name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "daily_count": self.daily_actions
        }
        self.logger.info(f"Action logged: {log_entry}")
        self.daily_actions += 1
        self.last_action_time = datetime.now()
        return log_entry

    def check_rate_limits(self) -> bool:
        """Check if we're within safe rate limits"""
        # Simple daily limit check
        if self.daily_actions >= 20:  # Conservative daily limit
            self.logger.warning(f"Daily limit reached for {self.name}")
            return False
        return True

    async def safe_execute(self, action_func, *args, **kwargs):
        """Execute action with safety checks and logging"""
        if not self.check_rate_limits():
            return {"status": "rate_limited", "platform": self.name}

        try:
            await self.simulate_human_delay()
            result = await action_func(*args, **kwargs)
            return self.log_action(action_func.__name__, result)
        except Exception as e:
            error_result = {"status": "error", "error": str(e), "platform": self.name}
            return self.log_action("error", error_result)
