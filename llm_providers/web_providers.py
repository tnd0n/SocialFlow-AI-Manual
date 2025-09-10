# Perplexity web automation provider
import asyncio
import json
from typing import List, Dict
from llm_providers.web_provider import WebLLMProvider
from backend.utils.logger import get_logger

log = get_logger("PerplexityWeb")

class PerplexityWebProvider(WebLLMProvider):
    """Perplexity AI web interface automation"""

    def __init__(self):
        super().__init__(
            name="perplexity_web",
            base_url="https://www.perplexity.ai/",
            cookie_file="perplexity_cookies.json"
        )
        self.max_daily_usage = 25  # Perplexity free tier limit

    async def navigate_to_chat(self):
        """Navigate to Perplexity chat interface"""
        await self.page.goto("https://www.perplexity.ai/")
        await asyncio.sleep(3)

        # Check if we need to log in
        try:
            # Look for sign-in button
            sign_in_button = await self.page.query_selector('button:has-text("Sign In")')
            if sign_in_button:
                log.warning("Perplexity requires login - cookies may be expired")
                # We'll continue anyway and see if it works
        except:
            pass

    async def send_prompt(self, prompt: str) -> str:
        """Send prompt to Perplexity and get response"""
        try:
            # Find the text input area
            input_selector = 'textarea[placeholder*="Ask anything"]'
            await self.page.wait_for_selector(input_selector, timeout=10000)

            # Clear and type prompt
            await self.page.fill(input_selector, prompt)
            await asyncio.sleep(1)

            # Submit the prompt
            submit_button = await self.page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
            else:
                # Try pressing Enter
                await self.page.keyboard.press('Enter')

            # Wait for response
            await asyncio.sleep(5)

            # Wait for response to complete (look for new message)
            await self.page.wait_for_selector('[data-testid="copilot-response"]', timeout=30000)
            await asyncio.sleep(3)  # Additional wait for completion

            # Extract response text
            response_elements = await self.page.query_selector_all('[data-testid="copilot-response"]')

            if response_elements:
                # Get the last response
                response_element = response_elements[-1]
                response_text = await response_element.inner_text()

                log.info(f"Perplexity response length: {len(response_text)} chars")
                return response_text.strip()
            else:
                # Fallback: get any text from response area
                response_area = await self.page.query_selector('.prose, .markdown, [class*="response"]')
                if response_area:
                    response_text = await response_area.inner_text()
                    return response_text.strip()
                else:
                    log.warning("No response found, returning page content")
                    return await self.page.inner_text('main, body')

        except Exception as e:
            log.error(f"Perplexity prompt failed: {e}")
            # Try to get any content from the page
            try:
                page_content = await self.page.inner_text('body')
                if "sign" in page_content.lower() or "login" in page_content.lower():
                    raise RuntimeError("Perplexity requires login - cookies expired")
                return page_content[:1000]  # Return first 1000 chars as fallback
            except:
                raise RuntimeError(f"Perplexity automation failed: {e}")

class ChatGPTWebProvider(WebLLMProvider):
    """ChatGPT web interface automation"""

    def __init__(self):
        super().__init__(
            name="chatgpt_web", 
            base_url="https://chat.openai.com/",
            cookie_file="chatgpt_cookies.json"
        )
        self.max_daily_usage = 40  # ChatGPT free tier limit

    async def navigate_to_chat(self):
        """Navigate to ChatGPT chat interface"""
        await self.page.goto("https://chat.openai.com/")
        await asyncio.sleep(3)

        # Check if logged in
        try:
            login_elements = await self.page.query_selector_all('button:has-text("Log in"), a:has-text("Log in")')
            if login_elements:
                log.warning("ChatGPT requires login - cookies may be expired")
        except:
            pass

    async def send_prompt(self, prompt: str) -> str:
        """Send prompt to ChatGPT and get response"""
        try:
            # Find the prompt input
            input_selector = 'textarea[placeholder*="Message"], #prompt-textarea'
            await self.page.wait_for_selector(input_selector, timeout=10000)

            # Type prompt
            await self.page.fill(input_selector, prompt)
            await asyncio.sleep(1)

            # Submit
            send_button = await self.page.query_selector('button[data-testid="send-button"]')
            if send_button:
                await send_button.click()
            else:
                await self.page.keyboard.press('Enter')

            # Wait for response
            await asyncio.sleep(3)

            # Wait for response completion
            await self.page.wait_for_selector('[data-message-author-role="assistant"]', timeout=45000)
            await asyncio.sleep(2)

            # Get response
            response_elements = await self.page.query_selector_all('[data-message-author-role="assistant"]')

            if response_elements:
                response_element = response_elements[-1]
                response_text = await response_element.inner_text()

                log.info(f"ChatGPT response length: {len(response_text)} chars")
                return response_text.strip()
            else:
                log.warning("No ChatGPT response found")
                return await self.page.inner_text('.conversation-content, main')

        except Exception as e:
            log.error(f"ChatGPT prompt failed: {e}")
            try:
                page_content = await self.page.inner_text('body')
                if any(word in page_content.lower() for word in ["login", "sign in", "authenticate"]):
                    raise RuntimeError("ChatGPT requires login - cookies expired")
                return page_content[:1000]
            except:
                raise RuntimeError(f"ChatGPT automation failed: {e}")

class GeminiWebProvider(WebLLMProvider):
    """Google Gemini web interface automation"""

    def __init__(self):
        super().__init__(
            name="gemini_web",
            base_url="https://gemini.google.com/",
            cookie_file="gemini_cookies.json" 
        )
        self.max_daily_usage = 60  # Gemini free tier limit

    async def navigate_to_chat(self):
        """Navigate to Gemini chat interface"""
        await self.page.goto("https://gemini.google.com/app")
        await asyncio.sleep(3)

        # Check for Google login
        try:
            if "accounts.google.com" in self.page.url:
                log.warning("Gemini requires Google login - cookies may be expired")
        except:
            pass

    async def send_prompt(self, prompt: str) -> str:
        """Send prompt to Gemini and get response"""
        try:
            # Find input area
            input_selector = 'div[contenteditable="true"], textarea'
            await self.page.wait_for_selector(input_selector, timeout=10000)

            # Type prompt
            await self.page.click(input_selector)
            await self.page.fill(input_selector, prompt)
            await asyncio.sleep(1)

            # Submit
            send_button = await self.page.query_selector('button[aria-label*="Send"], button[type="submit"]')
            if send_button:
                await send_button.click()
            else:
                await self.page.keyboard.press('Enter')

            # Wait for response
            await asyncio.sleep(5)

            # Wait for response to appear
            await self.page.wait_for_selector('[data-response-id], .response-container', timeout=45000)
            await asyncio.sleep(2)

            # Extract response
            response_elements = await self.page.query_selector_all('[data-response-id], .model-response')

            if response_elements:
                response_element = response_elements[-1]
                response_text = await response_element.inner_text()

                log.info(f"Gemini response length: {len(response_text)} chars")
                return response_text.strip()
            else:
                # Fallback
                main_content = await self.page.inner_text('main, [role="main"]')
                return main_content[:1000]

        except Exception as e:
            log.error(f"Gemini prompt failed: {e}")
            try:
                page_content = await self.page.inner_text('body')
                if "sign in" in page_content.lower() or "google" in page_content.lower():
                    raise RuntimeError("Gemini requires Google login - cookies expired")
                return page_content[:1000]
            except:
                raise RuntimeError(f"Gemini automation failed: {e}")
