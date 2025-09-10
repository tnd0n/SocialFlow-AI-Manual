# Threads automation engine for SocialFlow AI
import asyncio
import os
import json
from typing import Dict, List, Any
from playwright.async_api import async_playwright
from platforms.base_platform import BasePlatform
import requests

class ThreadsExecutor(BasePlatform):
    """Threads automation using web automation (Playwright)"""

    def __init__(self):
        super().__init__("threads")
        self.username = None
        self.password = None
        self.authenticated = False
        self.browser = None
        self.page = None

    async def authenticate(self) -> bool:
        """Authenticate with Threads using web session"""
        try:
            self.username = os.getenv("INSTAGRAM_USERNAME")  # Threads uses Instagram login
            self.password = os.getenv("INSTAGRAM_PASSWORD")

            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            context = await self.browser.new_context()

            # Load existing cookies if available
            cookies_file = "accounts/threads_cookies.json"
            if os.path.exists(cookies_file):
                with open(cookies_file, 'r') as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)

            self.page = await context.new_page()

            # Go to Threads
            await self.page.goto("https://www.threads.net/")
            await asyncio.sleep(3)

            # Check if already logged in
            if "login" not in self.page.url:
                self.authenticated = True
                self.logger.info("Threads already authenticated via cookies")
                return True

            # Login process
            await self.page.click('text="Log in"')
            await asyncio.sleep(2)

            # Fill login form
            await self.page.fill('input[name="username"]', self.username)
            await self.page.fill('input[name="password"]', self.password)
            await self.page.click('button[type="submit"]')

            # Wait for navigation
            await self.page.wait_for_url("https://www.threads.net/", timeout=10000)

            # Save cookies
            cookies = await context.cookies()
            os.makedirs("accounts", exist_ok=True)
            with open(cookies_file, 'w') as f:
                json.dump(cookies, f)

            self.authenticated = True
            self.logger.info("Threads authentication successful")
            return True

        except Exception as e:
            self.logger.error(f"Threads authentication failed: {e}")
            return False

    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Threads post"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # Navigate to compose
            await self.page.goto("https://www.threads.net/")
            await asyncio.sleep(2)

            # Click compose button
            await self.page.click('[aria-label="Create post"]')
            await asyncio.sleep(1)

            # Type content
            await self.page.fill('textarea[placeholder="Start a thread..."]', content["content"])
            await asyncio.sleep(2)

            # Add hashtags if provided
            if "hashtags" in content and content["hashtags"]:
                hashtags_text = " " + " ".join(content["hashtags"])
                await self.page.type('textarea[placeholder="Start a thread..."]', hashtags_text)

            # Post
            await self.page.click('button:has-text("Post")')
            await asyncio.sleep(3)

            # Get post URL (simplified - would need more robust detection)
            current_url = self.page.url

            result = {
                "status": "success",
                "content": content["content"],
                "hashtags": content.get("hashtags", []),
                "post_url": current_url
            }

            self.logger.info(f"Threads post created: {result['post_url']}")
            return result

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def engage_with_content(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Engage with Threads posts (like, comment)"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # Navigate to post
            if "post_url" in target:
                await self.page.goto(target["post_url"])
                await asyncio.sleep(2)

                # Add comment if specified
                if "comment" in target:
                    await self.page.click('[aria-label="Reply"]')
                    await asyncio.sleep(1)
                    await self.page.fill('textarea', target["comment"])
                    await self.page.click('button:has-text("Post")')
                    await asyncio.sleep(2)

                # Like the post
                await self.page.click('[aria-label="Like"]')

                return {
                    "status": "success",
                    "action": "engaged",
                    "post_url": target["post_url"]
                }

            return {"status": "failed", "error": "No post URL provided"}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def monitor_hashtags(self, hashtags: List[str]) -> List[Dict]:
        """Monitor hashtags for trending content"""
        if not self.authenticated:
            await self.authenticate()

        trending_posts = []

        try:
            for hashtag in hashtags[:3]:  # Limit to avoid detection
                try:
                    # Search for hashtag
                    search_url = f"https://www.threads.net/search?q=%23{hashtag.replace('#', '')}"
                    await self.page.goto(search_url)
                    await asyncio.sleep(3)

                    # Scroll to load more content
                    for _ in range(3):
                        await self.page.keyboard.press("PageDown")
                        await asyncio.sleep(2)

                    # Extract post information (simplified)
                    posts = await self.page.query_selector_all('article')

                    for post in posts[:5]:  # Limit per hashtag
                        try:
                            # Extract basic info (this would need more robust selectors)
                            text_content = await post.inner_text()
                            links = await post.query_selector_all('a')

                            if links:
                                post_link = await links[0].get_attribute('href')
                                trending_posts.append({
                                    "hashtag": hashtag,
                                    "content_preview": text_content[:200],
                                    "post_url": f"https://www.threads.net{post_link}",
                                    "discovered_at": asyncio.get_event_loop().time()
                                })
                        except:
                            continue

                    await asyncio.sleep(5)  # Delay between hashtags

                except Exception as e:
                    self.logger.warning(f"Failed to monitor hashtag {hashtag}: {e}")
                    continue

            return trending_posts

        except Exception as e:
            self.logger.error(f"Failed to monitor hashtags: {e}")
            return []

    async def scroll_feed(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """Simulate human-like feed scrolling"""
        if not self.authenticated:
            await self.authenticate()

        try:
            await self.page.goto("https://www.threads.net/")
            await asyncio.sleep(2)

            scroll_count = 0
            end_time = asyncio.get_event_loop().time() + (duration_minutes * 60)

            while asyncio.get_event_loop().time() < end_time:
                # Random scroll behavior
                await self.page.keyboard.press("PageDown")
                await asyncio.sleep(asyncio.get_event_loop().time() % 3 + 1)  # 1-4 seconds

                scroll_count += 1

                # Occasionally like a post
                if scroll_count % 5 == 0:
                    try:
                        like_buttons = await self.page.query_selector_all('[aria-label="Like"]')
                        if like_buttons:
                            await like_buttons[0].click()
                            await asyncio.sleep(1)
                    except:
                        pass

            return {
                "status": "success",
                "duration_minutes": duration_minutes,
                "scroll_count": scroll_count,
                "interactions": scroll_count // 5
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
