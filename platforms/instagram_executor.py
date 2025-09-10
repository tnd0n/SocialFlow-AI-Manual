# Instagram automation engine for SocialFlow AI
import os
import asyncio
import json
from typing import Dict, List, Any
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from platforms.base_platform import BasePlatform
import requests

class InstagramExecutor(BasePlatform):
    """Instagram automation using instagrapi library"""

    def __init__(self):
        super().__init__("instagram")
        self.client = Client()
        self.username = None
        self.password = None
        self.authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate with Instagram"""
        try:
            self.username = os.getenv("INSTAGRAM_USERNAME")
            self.password = os.getenv("INSTAGRAM_PASSWORD")

            # Try to load existing session
            session_file = "accounts/instagram_session.json"
            if os.path.exists(session_file):
                self.client.load_settings(session_file)

            # Login
            self.client.login(self.username, self.password)

            # Save session
            os.makedirs("accounts", exist_ok=True)
            self.client.dump_settings(session_file)

            self.authenticated = True
            self.logger.info(f"Instagram authenticated as: {self.username}")
            return True

        except (LoginRequired, ChallengeRequired) as e:
            self.logger.error(f"Instagram authentication failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Instagram error: {e}")
            return False

    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create Instagram post"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # For now, we'll focus on commenting rather than posting
            # Posting requires media files which need separate handling

            return {
                "status": "skipped",
                "reason": "Instagram posting requires media files - focus on commenting",
                "platform": "instagram"
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def engage_with_content(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Comment on Instagram posts"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # Extract username from account (remove @)
            username = target["account"].replace("@", "")

            # Get user ID
            user_id = self.client.user_id_from_username(username)

            # Get recent posts
            medias = self.client.user_medias(user_id, amount=5)

            # Find post matching keyword
            target_media = None
            keyword = target.get("recent_post_keyword", "")

            for media in medias:
                if keyword.lower() in media.caption_text.lower():
                    target_media = media
                    break

            if not target_media and medias:
                # If no keyword match, use most recent post
                target_media = medias[0]

            if target_media:
                # Add comment
                comment = self.client.media_comment(
                    target_media.id, 
                    target["comment"]
                )

                result = {
                    "status": "success",
                    "account": target["account"],
                    "post_id": target_media.id,
                    "post_url": f"https://instagram.com/p/{target_media.code}/",
                    "comment_id": comment.pk,
                    "comment_text": target["comment"]
                }

                self.logger.info(f"Instagram comment added: {result['post_url']}")
                return result
            else:
                return {
                    "status": "no_target",
                    "account": target["account"],
                    "reason": "No matching posts found"
                }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "account": target.get("account", "unknown")
            }

    async def discover_viral_posts(self, hashtags: List[str], limit: int = 20) -> List[Dict]:
        """Find viral posts by hashtags"""
        if not self.authenticated:
            await self.authenticate()

        viral_posts = []

        try:
            for hashtag in hashtags[:3]:  # Limit to avoid rate limits
                try:
                    # Get hashtag media
                    medias = self.client.hashtag_medias_recent(hashtag, amount=limit)

                    for media in medias:
                        # Filter by engagement (likes + comments)
                        engagement = media.like_count + media.comment_count

                        if engagement > 1000:  # Viral threshold
                            viral_posts.append({
                                "id": media.id,
                                "code": media.code,
                                "url": f"https://instagram.com/p/{media.code}/",
                                "caption": media.caption_text[:200],
                                "likes": media.like_count,
                                "comments": media.comment_count,
                                "engagement": engagement,
                                "hashtag": hashtag,
                                "username": media.user.username
                            })

                    # Delay between hashtag searches
                    await asyncio.sleep(10)

                except Exception as e:
                    self.logger.warning(f"Failed to search hashtag {hashtag}: {e}")
                    continue

            # Sort by engagement
            viral_posts.sort(key=lambda x: x["engagement"], reverse=True)
            return viral_posts[:limit]

        except Exception as e:
            self.logger.error(f"Failed to discover viral posts: {e}")
            return []

    async def get_account_insights(self, username: str) -> Dict[str, Any]:
        """Get insights about an Instagram account"""
        if not self.authenticated:
            await self.authenticate()

        try:
            user_info = self.client.user_info_by_username(username)

            return {
                "username": user_info.username,
                "followers": user_info.follower_count,
                "following": user_info.following_count,
                "posts": user_info.media_count,
                "verified": user_info.is_verified,
                "business": user_info.is_business,
                "biography": user_info.biography
            }

        except Exception as e:
            return {"error": str(e), "username": username}
