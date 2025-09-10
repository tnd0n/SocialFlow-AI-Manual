#!/usr/bin/env python3
"""
Cookie Setup Helper for SocialFlow AI Web Providers
Run this once to capture login cookies for Perplexity, ChatGPT, and Gemini
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

class CookieSetupHelper:
    """Helper to setup authentication cookies for web providers"""

    def __init__(self):
        self.accounts_dir = Path("accounts")
        self.accounts_dir.mkdir(exist_ok=True)

    async def setup_perplexity_cookies(self):
        """Setup Perplexity authentication cookies"""
        print("🔮 Setting up Perplexity cookies...")
        print("1. Browser will open to Perplexity")
        print("2. Log in with your account")
        print("3. Close the browser when done")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.perplexity.ai/")

        # Wait for user to login
        print("\n⏳ Please log in to Perplexity and press Enter when done...")
        input()

        # Save cookies
        cookies = await context.cookies()
        cookie_file = self.accounts_dir / "perplexity_cookies.json"

        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Perplexity cookies saved to {cookie_file}")
        print(f"   Saved {len(cookies)} cookies")

        await browser.close()
        await playwright.stop()

    async def setup_chatgpt_cookies(self):
        """Setup ChatGPT authentication cookies"""
        print("🤖 Setting up ChatGPT cookies...")
        print("1. Browser will open to ChatGPT")
        print("2. Log in with your OpenAI account")
        print("3. Close the browser when done")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://chat.openai.com/")

        print("\n⏳ Please log in to ChatGPT and press Enter when done...")
        input()

        cookies = await context.cookies()
        cookie_file = self.accounts_dir / "chatgpt_cookies.json"

        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ ChatGPT cookies saved to {cookie_file}")
        print(f"   Saved {len(cookies)} cookies")

        await browser.close()
        await playwright.stop()

    async def setup_gemini_cookies(self):
        """Setup Gemini authentication cookies"""
        print("💎 Setting up Gemini cookies...")
        print("1. Browser will open to Gemini")
        print("2. Log in with your Google account")
        print("3. Close the browser when done")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://gemini.google.com/app")

        print("\n⏳ Please log in to Gemini and press Enter when done...")
        input()

        cookies = await context.cookies()
        cookie_file = self.accounts_dir / "gemini_cookies.json"

        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Gemini cookies saved to {cookie_file}")
        print(f"   Saved {len(cookies)} cookies")

        await browser.close()
        await playwright.stop()

    async def test_all_cookies(self):
        """Test all saved cookies"""
        print("🧪 Testing all saved cookies...")

        from llm_providers.web_providers import PerplexityWebProvider, ChatGPTWebProvider, GeminiWebProvider

        providers = [
            ("Perplexity", PerplexityWebProvider()),
            ("ChatGPT", ChatGPTWebProvider()),
            ("Gemini", GeminiWebProvider())
        ]

        test_prompt = [{"role": "user", "content": "Hello! Please respond with 'Authentication test successful'"}]

        for name, provider in providers:
            try:
                print(f"\n🔍 Testing {name}...")
                response = await provider.chat(test_prompt)
                if "successful" in response.lower() or len(response) > 10:
                    print(f"✅ {name}: Working")
                else:
                    print(f"⚠️ {name}: Unexpected response - {response[:50]}...")

            except Exception as e:
                print(f"❌ {name}: Failed - {e}")
            finally:
                if hasattr(provider, 'cleanup'):
                    await provider.cleanup()

    async def setup_all(self):
        """Setup all web provider cookies"""
        print("🚀 SocialFlow AI - Web Provider Cookie Setup")
        print("=" * 50)

        choice = input("""
Which providers would you like to set up?
1. Perplexity only
2. ChatGPT only  
3. Gemini only
4. All providers
5. Test existing cookies

Enter your choice (1-5): """)

        if choice == "1":
            await self.setup_perplexity_cookies()
        elif choice == "2":
            await self.setup_chatgpt_cookies()
        elif choice == "3":
            await self.setup_gemini_cookies()
        elif choice == "4":
            await self.setup_perplexity_cookies()
            await self.setup_chatgpt_cookies()
            await self.setup_gemini_cookies()
        elif choice == "5":
            await self.test_all_cookies()
        else:
            print("Invalid choice")
            return

        if choice in ["1", "2", "3", "4"]:
            test_choice = input("\nWould you like to test the cookies now? (y/n): ")
            if test_choice.lower() == "y":
                await self.test_all_cookies()

        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Run: python core/content_scheduler.py --test")
        print("2. Run: python core/content_scheduler.py")
        print("3. Check content_queue/ for generated content")

async def main():
    helper = CookieSetupHelper()
    await helper.setup_all()

if __name__ == "__main__":
    asyncio.run(main())
