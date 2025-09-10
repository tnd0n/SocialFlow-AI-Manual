# Telegram automation engine for SocialFlow AI  
import asyncio
import os
import json
from typing import Dict, List, Any
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendMessageRequest
from platforms.base_platform import BasePlatform

class TelegramExecutor(BasePlatform):
    """Telegram automation using Telethon + Bot API"""

    def __init__(self):
        super().__init__("telegram")
        self.client = None
        self.api_id = None
        self.api_hash = None
        self.bot_token = None
        self.authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate with Telegram using bot token (non-interactive)"""
        try:
            self.api_id = int(os.getenv("TELEGRAM_API_ID"))
            self.api_hash = os.getenv("TELEGRAM_API_HASH")
            self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

            if not self.bot_token:
                self.logger.error("TELEGRAM_BOT_TOKEN not found in environment")
                return False

            # Initialize Telethon client with bot token (no phone verification needed)
            self.client = TelegramClient('socialflow_bot_session', self.api_id, self.api_hash)

            # Start client with bot token (non-interactive)
            await self.client.start(bot_token=self.bot_token)

            # Verify authentication
            me = await self.client.get_me()
            self.authenticated = True
            self.logger.info(f"Telegram bot authenticated as: {me.username or me.first_name}")
            return True

        except Exception as e:
            self.logger.error(f"Telegram authentication failed: {e}")
            # Try fallback with session file if bot auth fails
            try:
                # Check if session file exists and try user authentication
                session_path = "accounts/telegram_session.session"
                phone = os.getenv("TELEGRAM_PHONE")
                
                if os.path.exists(session_path) and phone:
                    self.client = TelegramClient(session_path, self.api_id, self.api_hash)
                    await self.client.start(phone=phone)
                    me = await self.client.get_me()
                    self.authenticated = True
                    self.logger.info(f"Telegram user authenticated as: {me.username or me.first_name}")
                    return True
                else:
                    self.logger.warning("No existing session file found and phone not provided")
                    return False
                    
            except Exception as fallback_error:
                self.logger.error(f"Telegram fallback authentication failed: {fallback_error}")
                # Try to connect to existing session without phone if it exists
                try:
                    session_path = "accounts/telegram_session.session"
                    if os.path.exists(session_path):
                        self.client = TelegramClient(session_path, self.api_id, self.api_hash)
                        await self.client.connect()
                        if await self.client.is_user_authorized():
                            me = await self.client.get_me()
                            self.authenticated = True
                            self.logger.info(f"Telegram session restored: {me.username or me.first_name}")
                            return True
                except Exception as session_error:
                    self.logger.error(f"Session restore failed: {session_error}")
                
                return False

    async def post_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Telegram groups/channels"""
        if not self.authenticated:
            auth_success = await self.authenticate()
            if not auth_success:
                return {
                    "status": "failed",
                    "error": "Authentication failed - check Telegram API credentials"
                }

        results = []

        try:
            for target in content.get("target_groups", []):
                try:
                    # Send message
                    message = await self.client.send_message(
                        target, 
                        content["content"]
                    )

                    result = {
                        "status": "success",
                        "target": target,
                        "message_id": message.id,
                        "message_link": f"https://t.me/{target.replace('@', '')}/{message.id}"
                    }
                    results.append(result)

                    # Delay between groups
                    await asyncio.sleep(30)

                except Exception as e:
                    results.append({
                        "status": "failed",
                        "target": target, 
                        "error": str(e)
                    })

            return {"platform": "telegram", "results": results}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def engage_with_content(self, target: Dict[str, Any]) -> Dict[str, Any]:
        """Reply to Telegram messages"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # Get the message to reply to
            entity = await self.client.get_entity(target["group"])

            # Send reply
            if "reply_to_message_id" in target:
                message = await self.client.send_message(
                    entity,
                    target["reply_content"],
                    reply_to=target["reply_to_message_id"]
                )
            else:
                message = await self.client.send_message(entity, target["content"])

            return {
                "status": "success",
                "message_id": message.id,
                "group": target["group"]
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def join_group(self, group_link: str) -> Dict[str, Any]:
        """Join a Telegram group/channel (Note: Not supported for bot accounts)"""
        if not self.authenticated:
            await self.authenticate()

        # Check if using bot authentication (bots cannot self-join groups)
        if self.bot_token:
            return {
                "status": "failed",
                "error": "Bot accounts cannot join groups automatically. Manual addition required."
            }

        try:
            # Extract username from link
            if "t.me/" in group_link:
                username = group_link.split("t.me/")[1]
            else:
                username = group_link

            # Join the channel/group
            entity = await self.client.get_entity(username)
            await self.client(JoinChannelRequest(entity))

            return {
                "status": "success",
                "group": username,
                "action": "joined"
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "group": group_link
            }

    async def discover_active_groups(self, keywords: List[str]) -> List[Dict]:
        """Find active groups related to keywords"""
        if not self.authenticated:
            await self.authenticate()

        # Note: This is a simplified version
        # Real implementation would use Telegram's search functionality
        active_groups = []

        try:
            # Get user's dialogs (groups they're in)
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group or dialog.is_channel:
                    for keyword in keywords:
                        if keyword.lower() in dialog.name.lower():
                            active_groups.append({
                                "name": dialog.name,
                                "username": dialog.entity.username,
                                "members": getattr(dialog.entity, 'participants_count', 0)
                            })

            return active_groups

        except Exception as e:
            self.logger.error(f"Failed to discover groups: {e}")
            return []

    async def monitor_mentions(self) -> List[Dict]:
        """Monitor mentions and keywords in groups"""
        mentions = []

        # This would be implemented with event handlers
        # @self.client.on(events.NewMessage)
        # For now, return empty list

        return mentions

    async def disconnect(self):
        """Properly disconnect the client"""
        if self.client:
            await self.client.disconnect()
