# SocialFlow AI - Posting Status Check Utilities
import praw
from telethon import TelegramClient
from instagrapi import Client as InstaClient
from asyncio import run

class StatusChecker:
    def __init__(self, reddit_creds, telegram_creds, instagram_creds):
        # Initialize clients
        self.reddit = praw.Reddit(
            client_id=reddit_creds['client_id'],
            client_secret=reddit_creds['client_secret'],
            username=reddit_creds['username'],
            password=reddit_creds['password'],
            user_agent='SocialFlow AI StatusChecker'
        )

        self.telegram_client = TelegramClient('checker_session', telegram_creds['api_id'], telegram_creds['api_hash'])
        self.telegram_bot_token = telegram_creds['bot_token']

        self.instagram_client = InstaClient()
        self.instagram_username = instagram_creds['username']
        self.instagram_password = instagram_creds['password']

    def check_reddit_post(self, subreddit, title) -> bool:
        # Check if post with given title exists recently in subreddit
        subreddit_obj = self.reddit.subreddit(subreddit)
        for submission in subreddit_obj.new(limit=20):
            if submission.title == title:
                return True
        return False

    async def check_telegram_message(self, chat_id, content_substr) -> bool:
        await self.telegram_client.start()
        async for message in self.telegram_client.iter_messages(chat_id, limit=50):
            if content_substr in message.message:
                await self.telegram_client.disconnect()
                return True
        await self.telegram_client.disconnect()
        return False

    def instagram_login(self):
        self.instagram_client.login(self.instagram_username, self.instagram_password)

    def check_instagram_comment(self, post_shortcode, comment_substr) -> bool:
        # Login if not
        if not self.instagram_client.user_id:
            self.instagram_login()
        media = self.instagram_client.media_info(post_shortcode)
        comments = self.instagram_client.media_comments(media.pk)
        for c in comments:
            if comment_substr in c.text:
                return True
        return False

# Usage Example (fill creds):
# reddit_creds = {"client_id":"...","client_secret":"...","username":"...","password":"..."}
# telegram_creds = {"api_id":123456,"api_hash":"...","bot_token":"..."}
# instagram_creds = {"username":"...","password":"..."}
# checker = StatusChecker(reddit_creds, telegram_creds, instagram_creds)
# print(checker.check_reddit_post('algotrading', 'Open Source Trading Bot'))
# run(checker.check_telegram_message('@trading_group', 'update'))
# checker.check_instagram_comment('Cabc123', 'insightful')
