# Enhanced LLM manager with API + web provider fallback
import asyncio
import os
import random
from typing import List, Dict, Any, Optional

# Optional imports for API providers
try:
    from llm_providers.openai_provider import OpenAIProvider
except ImportError:
    OpenAIProvider = None

try:
    from llm_providers.perplexity_provider import PerplexityProvider
except ImportError:
    PerplexityProvider = None

try:
    from llm_providers.gemini_provider import GeminiProvider
except ImportError:
    GeminiProvider = None

from llm_providers.web_providers import PerplexityWebProvider, ChatGPTWebProvider, GeminiWebProvider
from backend.utils.logger import get_logger

log = get_logger("LLMManager")

class EnhancedLLMManager:
    """Enhanced LLM manager with API keys + web automation fallback"""

    def __init__(self):
        self.api_providers = []
        self.web_providers = []
        self.current_provider_index = 0
        self.daily_usage_tracking = {}

        # Initialize API providers
        self._init_api_providers()

        # Initialize web providers  
        self._init_web_providers()

        # Combine all providers in priority order
        self.all_providers = self.api_providers + self.web_providers

        log.info(f"Initialized {len(self.api_providers)} API + {len(self.web_providers)} web providers")

    def _init_api_providers(self):
        """Initialize API-based providers with multiple keys"""
        try:
            # OpenAI with multiple keys
            if OpenAIProvider:
                openai_keys = os.getenv("OPENAI_API_KEYS", "").split(",")
                for key in openai_keys:
                    if key.strip():
                        provider = OpenAIProvider()
                        provider.api_key = key.strip()
                        self.api_providers.append(provider)
        except Exception as e:
            log.warning(f"Failed to init OpenAI providers: {e}")

        try:
            # Perplexity with multiple keys
            if PerplexityProvider:
                perplexity_keys = os.getenv("PERPLEXITY_API_KEYS", "").split(",")
                for key in perplexity_keys:
                    if key.strip():
                        provider = PerplexityProvider()
                        provider.api_key = key.strip()
                        self.api_providers.append(provider)
        except Exception as e:
            log.warning(f"Failed to init Perplexity providers: {e}")

        try:
            # Gemini with multiple keys
            if GeminiProvider:
                gemini_keys = os.getenv("GEMINI_API_KEYS", "").split(",")
                for key in gemini_keys:
                    if key.strip():
                        provider = GeminiProvider()
                        provider.api_key = key.strip()
                        self.api_providers.append(provider)
        except Exception as e:
            log.warning(f"Failed to init Gemini providers: {e}")

    def _init_web_providers(self):
        """Initialize web-based providers"""
        try:
            # Only add if cookie files are configured
            if os.getenv("PERPLEXITY_COOKIE_FILE") or os.path.exists("accounts/perplexity_cookies.json"):
                self.web_providers.append(PerplexityWebProvider())

            if os.getenv("CHATGPT_COOKIE_FILE") or os.path.exists("accounts/chatgpt_cookies.json"):
                self.web_providers.append(ChatGPTWebProvider())

            if os.getenv("GEMINI_COOKIE_FILE") or os.path.exists("accounts/gemini_cookies.json"):
                self.web_providers.append(GeminiWebProvider())

        except Exception as e:
            log.warning(f"Failed to init web providers: {e}")

    async def smart_chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Try providers in order with intelligent fallback"""
        if not self.all_providers:
            raise RuntimeError("No LLM providers available")

        errors = []

        # Try API providers first (faster, more reliable)
        for provider in self.api_providers:
            try:
                if await self._check_provider_availability(provider):
                    response = await provider.chat(messages, **kwargs)
                    log.info(f"✅ {provider.name} succeeded")
                    await self._update_usage_tracking(provider)
                    return response
            except Exception as e:
                error_msg = f"{provider.name}: {str(e)[:100]}"
                errors.append(error_msg)
                log.warning(f"❌ {error_msg}")
                continue

        # Fallback to web providers if APIs failed
        for provider in self.web_providers:
            try:
                if await self._check_provider_availability(provider):
                    response = await provider.chat(messages, **kwargs)
                    log.info(f"✅ {provider.name} (web) succeeded")
                    await self._update_usage_tracking(provider)
                    return response
            except Exception as e:
                error_msg = f"{provider.name}: {str(e)[:100]}"
                errors.append(error_msg)
                log.warning(f"❌ {error_msg}")
                continue
            finally:
                # Always cleanup web providers
                if hasattr(provider, 'cleanup'):
                    try:
                        await provider.cleanup()
                    except:
                        pass

        # All providers failed
        raise RuntimeError(f"All LLM providers failed: {errors}")

    async def _check_provider_availability(self, provider) -> bool:
        """Check if provider is available (not rate limited)"""
        provider_id = f"{provider.name}_{getattr(provider, 'api_key', 'web')}"

        # Check daily usage
        today = asyncio.get_event_loop().time() // 86400  # days since epoch
        usage_key = f"{provider_id}_{today}"

        current_usage = self.daily_usage_tracking.get(usage_key, 0)
        max_usage = getattr(provider, 'max_daily_usage', 100)

        if current_usage >= max_usage:
            log.warning(f"{provider.name} daily limit reached: {current_usage}/{max_usage}")
            return False

        return True

    async def _update_usage_tracking(self, provider):
        """Update usage tracking for the provider"""
        provider_id = f"{provider.name}_{getattr(provider, 'api_key', 'web')}"
        today = asyncio.get_event_loop().time() // 86400
        usage_key = f"{provider_id}_{today}"

        self.daily_usage_tracking[usage_key] = self.daily_usage_tracking.get(usage_key, 0) + 1

        # Update provider's internal tracking if it exists
        if hasattr(provider, 'daily_usage'):
            provider.daily_usage += 1

    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {
            "api_providers": len(self.api_providers),
            "web_providers": len(self.web_providers),
            "total_providers": len(self.all_providers),
            "daily_usage": self.daily_usage_tracking,
            "provider_details": []
        }

        for provider in self.all_providers:
            provider_info = {
                "name": provider.name,
                "type": "api" if provider in self.api_providers else "web",
                "available": await self._check_provider_availability(provider)
            }

            if hasattr(provider, 'daily_usage'):
                provider_info["daily_usage"] = provider.daily_usage
            if hasattr(provider, 'max_daily_usage'):
                provider_info["max_daily_usage"] = provider.max_daily_usage

            status["provider_details"].append(provider_info)

        return status

    async def cleanup_all(self):
        """Cleanup all web providers"""
        for provider in self.web_providers:
            if hasattr(provider, 'cleanup'):
                try:
                    await provider.cleanup()
                except Exception as e:
                    log.warning(f"Cleanup failed for {provider.name}: {e}")

# Global enhanced manager instance
enhanced_llm_manager = EnhancedLLMManager()

async def smart_chat(messages: List[Dict[str, str]], **kwargs) -> str:
    """Enhanced smart chat with API + web fallback"""
    return await enhanced_llm_manager.smart_chat(messages, **kwargs)

async def get_llm_status() -> Dict[str, Any]:
    """Get status of all LLM providers"""
    return await enhanced_llm_manager.get_provider_status()

# For backward compatibility
async def cleanup_llm_resources():
    """Cleanup LLM resources"""
    await enhanced_llm_manager.cleanup_all()
