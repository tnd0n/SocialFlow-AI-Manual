# Web-based LLM provider using Playwright automation
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from llm_providers.base import LLMProvider
from backend.utils.logger import get_logger

log = get_logger("WebLLM")

class WebLLMProvider(LLMProvider):
    """Base class for web-based LLM providers using browser automation"""

    def __init__(self, name: str, base_url: str, cookie_file: str):
        super().__init__()
        self.name = name
        self.base_url = base_url
        self.cookie_file = Path(f"accounts/{cookie_file}")
        self.browser = None
        self.page = None
        self.daily_usage = 0
        self.max_daily_usage = 50  # Conservative limit

    async def start_browser(self):
        """Start browser session with saved cookies"""
        if self.browser:
            return

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

        # Load cookies if available
        if self.cookie_file.exists():
            try:
                with open(self.cookie_file, 'r') as f:
                    cookies = json.load(f)
                await context.add_cookies(cookies)
                log.info(f"Loaded {len(cookies)} cookies for {self.name}")
            except Exception as e:
                log.warning(f"Failed to load cookies for {self.name}: {e}")

        self.page = await context.new_page()

    async def save_cookies(self):
        """Save current session cookies"""
        if not self.page:
            return

        try:
            cookies = await self.page.context.cookies()
            self.cookie_file.parent.mkdir(exist_ok=True)
            with open(self.cookie_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            log.info(f"Saved {len(cookies)} cookies for {self.name}")
        except Exception as e:
            log.error(f"Failed to save cookies for {self.name}: {e}")

    async def check_rate_limits(self) -> bool:
        """Check if we're within daily limits"""
        if self.daily_usage >= self.max_daily_usage:
            log.warning(f"{self.name} daily limit reached: {self.daily_usage}/{self.max_daily_usage}")
            return False
        return True

    async def navigate_to_chat(self):
        """Navigate to chat interface - override in subclasses"""
        await self.page.goto(self.base_url)
        await asyncio.sleep(2)

    async def send_prompt(self, prompt: str) -> str:
        """Send prompt and get response - override in subclasses"""
        raise NotImplementedError("Subclass must implement send_prompt")

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Main chat interface"""
        if not await self.check_rate_limits():
            raise RuntimeError(f"{self.name} rate limit exceeded")

        if not self.browser:
            await self.start_browser()

        try:
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)

            # Navigate and send
            await self.navigate_to_chat()
            response = await self.send_prompt(prompt)

            # Update usage and save cookies
            self.daily_usage += 1
            await self.save_cookies()

            log.info(f"{self.name} response generated (usage: {self.daily_usage}/{self.max_daily_usage})")
            return response

        except Exception as e:
            log.error(f"{self.name} chat failed: {e}")
            raise

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to single prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"Instructions: {content}")
            elif role == "user":
                prompt_parts.append(content)
            elif role == "assistant":
                prompt_parts.append(f"Previous response: {content}")

        return "\n\n".join(prompt_parts)

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
