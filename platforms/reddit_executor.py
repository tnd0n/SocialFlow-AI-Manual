# Reddit automation engine for SocialFlow AI
import praw
import requests
import json
import os
import asyncio
from typing import Dict, List, Any
from platforms.base_platform import BasePlatform
from pathlib import Path

class RedditExecutor(BasePlatform):
    """Reddit automation using PRAW API + web sessions"""

    def __init__(self):
        super().__init__("reddit")
        self.reddit = None
        self.web_session = requests.Session()
        self.authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate using PRAW and web session"""
        try:
            # Load credentials
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET") 
            username = os.getenv("REDDIT_USERNAME")
            password = os.getenv("REDDIT_PASSWORD")

            # Initialize PRAW
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent="SocialFlow AI v1.0 by /u/{}".format(username)
            )

            # Test authentication
            self.reddit.user.me()
            self.authenticated = True
            self.logger.info("Reddit authentication successful")
            return True

        except Exception as e:
            self.logger.error(f"Reddit authentication failed: {e}")
            return False

    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Reddit post"""
        if not self.authenticated:
            await self.authenticate()

        try:
            subreddit = self.reddit.subreddit(content["subreddit"])

            # Create post
            submission = subreddit.submit(
                title=content["title"],
                selftext=content.get("content", "")
            )

            result = {
                "status": "success",
                "post_id": submission.id,
                "post_url": f"https://reddit.com{submission.permalink}",
                "subreddit": content["subreddit"],
                "title": content["title"]
            }

            self.logger.info(f"Reddit post created: {result['post_url']}")
            return result

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "subreddit": content.get("subreddit", "unknown")
            }

    async def engage_with_content(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Comment on Reddit posts"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # Get submission by ID or URL
            if "post_id" in target:
                submission = self.reddit.submission(id=target["post_id"])
            elif "post_url" in target:
                submission = self.reddit.submission(url=target["post_url"])
            else:
                return {"status": "failed", "error": "No post ID or URL provided"}

            # Add comment
            comment = submission.reply(target["comment"])

            result = {
                "status": "success", 
                "comment_id": comment.id,
                "post_id": submission.id,
                "comment_url": f"https://reddit.com{comment.permalink}"
            }

            self.logger.info(f"Reddit comment added: {result['comment_url']}")
            return result

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def discover_trending_posts(self, subreddit: str, limit: int = 10) -> List[Dict]:
        """Find trending posts in a subreddit"""
        if not self.authenticated:
            await self.authenticate()

        try:
            sub = self.reddit.subreddit(subreddit)
            trending = []

            for submission in sub.hot(limit=limit):
                trending.append({
                    "id": submission.id,
                    "title": submission.title,
                    "url": f"https://reddit.com{submission.permalink}",
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_utc": submission.created_utc
                })

            return trending

        except Exception as e:
            self.logger.error(f"Failed to get trending posts: {e}")
            return []

    async def join_subreddit(self, subreddit_name: str) -> Dict[str, Any]:
        """Join a subreddit"""
        if not self.authenticated:
            await self.authenticate()

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            subreddit.subscribe()

            return {
                "status": "success",
                "subreddit": subreddit_name,
                "action": "joined"
            }

        except Exception as e:
            return {
                "status": "failed", 
                "error": str(e),
                "subreddit": subreddit_name
            }
