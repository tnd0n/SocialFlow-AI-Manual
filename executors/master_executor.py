# Master executor for SocialFlow AI - orchestrates all platforms
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

from platforms.reddit_executor import RedditExecutor
from platforms.telegram_executor import TelegramExecutor
from platforms.threads_executor import ThreadsExecutor
from platforms.instagram_executor import InstagramExecutor

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('execution.log'),
        logging.StreamHandler()
    ]
)

class MasterExecutor:
    """Orchestrates content execution across all social media platforms"""

    def __init__(self):
        self.logger = logging.getLogger("MasterExecutor")

        # Initialize platform executors
        self.reddit = RedditExecutor()
        self.telegram = TelegramExecutor()
        self.threads = ThreadsExecutor()
        self.instagram = InstagramExecutor()

        self.execution_log = []
        self.daily_limits = {
            "reddit_posts": 3,
            "telegram_messages": 5,
            "threads_posts": 4,
            "instagram_comments": 8,
            "total_actions": 20
        }

    async def load_content_queue(self, queue_file: str) -> Dict[str, Any]:
        """Load content from queue file"""
        file_path = Path("content_queue") / queue_file

        if not file_path.exists():
            self.logger.warning(f"Queue file not found: {queue_file}")
            return {}

        try:
            with open(file_path, 'r') as f:
                content = json.load(f)

            if content.get("execution_status") == "completed":
                self.logger.info(f"Queue {queue_file} already completed")
                return {}

            return content

        except Exception as e:
            self.logger.error(f"Failed to load queue {queue_file}: {e}")
            return {}

    async def execute_reddit_queue(self) -> List[Dict]:
        """Execute Reddit content queue"""
        queue = await self.load_content_queue("reddit_queue.json")
        results = []

        if not queue.get("reddit_posts"):
            return results

        posts = queue["reddit_posts"][:self.daily_limits["reddit_posts"]]

        for post in posts:
            try:
                self.logger.info(f"Executing Reddit post: {post['title'][:50]}...")

                result = await self.reddit.safe_execute(
                    self.reddit.post_content, 
                    post
                )

                results.append(result)

                # Human-like delay between posts
                delay = random.randint(300, 1800)  # 5-30 minutes
                self.logger.info(f"Waiting {delay}s before next Reddit action...")
                await asyncio.sleep(delay)

            except Exception as e:
                self.logger.error(f"Reddit post failed: {e}")
                results.append({"status": "error", "error": str(e), "platform": "reddit"})

        return results

    async def execute_telegram_queue(self) -> List[Dict]:
        """Execute Telegram content queue"""
        queue = await self.load_content_queue("telegram_queue.json")
        results = []

        if not queue.get("telegram_messages"):
            return results

        messages = queue["telegram_messages"][:self.daily_limits["telegram_messages"]]

        for message in messages:
            try:
                self.logger.info(f"Executing Telegram message to {len(message.get('target_groups', []))} groups...")

                result = await self.telegram.safe_execute(
                    self.telegram.post_content,
                    message
                )

                results.append(result)

                # Delay between message batches
                delay = random.randint(600, 1800)  # 10-30 minutes
                self.logger.info(f"Waiting {delay}s before next Telegram action...")
                await asyncio.sleep(delay)

            except Exception as e:
                self.logger.error(f"Telegram message failed: {e}")
                results.append({"status": "error", "error": str(e), "platform": "telegram"})

        return results

    async def execute_threads_queue(self) -> List[Dict]:
        """Execute Threads content queue"""
        queue = await self.load_content_queue("threads_queue.json")
        results = []

        if not queue.get("threads_posts"):
            return results

        posts = queue["threads_posts"][:self.daily_limits["threads_posts"]]

        for post in posts:
            try:
                self.logger.info(f"Executing Threads post with {len(post.get('hashtags', []))} hashtags...")

                result = await self.threads.safe_execute(
                    self.threads.post_content,
                    post
                )

                results.append(result)

                # Delay between posts
                delay = random.randint(900, 2700)  # 15-45 minutes
                self.logger.info(f"Waiting {delay}s before next Threads action...")
                await asyncio.sleep(delay)

            except Exception as e:
                self.logger.error(f"Threads post failed: {e}")
                results.append({"status": "error", "error": str(e), "platform": "threads"})

        return results

    async def execute_instagram_queue(self) -> List[Dict]:
        """Execute Instagram content queue"""
        queue = await self.load_content_queue("instagram_queue.json")
        results = []

        if not queue.get("instagram_targets"):
            return results

        targets = queue["instagram_targets"][:self.daily_limits["instagram_comments"]]

        for target in targets:
            try:
                self.logger.info(f"Executing Instagram comment on {target['account']}...")

                result = await self.instagram.safe_execute(
                    self.instagram.engage_with_content,
                    target
                )

                results.append(result)

                # Delay between comments
                delay = random.randint(300, 900)  # 5-15 minutes
                self.logger.info(f"Waiting {delay}s before next Instagram action...")
                await asyncio.sleep(delay)

            except Exception as e:
                self.logger.error(f"Instagram comment failed: {e}")
                results.append({"status": "error", "error": str(e), "platform": "instagram"})

        return results

    async def execute_daily_batch(self) -> Dict[str, Any]:
        """Execute complete daily content batch across all platforms"""
        start_time = datetime.now()
        self.logger.info("🚀 Starting daily SocialFlow execution batch")

        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv("config/accounts.env")

        all_results = []

        try:
            # Morning: Reddit posts (9-11 AM optimal)
            self.logger.info("📝 Executing Reddit queue...")
            reddit_results = await self.execute_reddit_queue()
            all_results.extend(reddit_results)

            # Afternoon: Telegram messages (2-4 PM optimal)
            self.logger.info("📱 Executing Telegram queue...")
            telegram_results = await self.execute_telegram_queue()
            all_results.extend(telegram_results)

            # Evening: Threads posts (7-9 PM optimal) 
            self.logger.info("🧵 Executing Threads queue...")
            threads_results = await self.execute_threads_queue()
            all_results.extend(threads_results)

            # Night: Instagram comments (10 PM-12 AM optimal)
            self.logger.info("📸 Executing Instagram queue...")
            instagram_results = await self.execute_instagram_queue()
            all_results.extend(instagram_results)

            # Generate execution summary
            execution_summary = {
                "execution_date": start_time.isoformat(),
                "duration_minutes": (datetime.now() - start_time).total_seconds() / 60,
                "platforms_executed": len([r for r in all_results if r.get("status") == "success"]),
                "total_actions": len(all_results),
                "success_rate": len([r for r in all_results if r.get("status") == "success"]) / len(all_results) if all_results else 0,
                "results": all_results
            }

            # Save execution log
            await self.save_execution_log(execution_summary)

            # Archive completed queues
            await self.archive_completed_queues()

            self.logger.info(f"✅ Daily execution completed: {execution_summary['success_rate']:.1%} success rate")
            return execution_summary

        except Exception as e:
            self.logger.error(f"❌ Daily execution failed: {e}")
            return {
                "execution_date": start_time.isoformat(),
                "status": "failed",
                "error": str(e),
                "results": all_results
            }

        finally:
            # Cleanup resources
            await self.cleanup_resources()

    async def save_execution_log(self, summary: Dict[str, Any]):
        """Save execution results to log file"""
        try:
            log_file = Path("EXECUTION_LOG.md")

            # Create log entry
            log_entry = f"""
## {summary['execution_date'][:10]} - Daily Execution

**Duration**: {summary['duration_minutes']:.1f} minutes  
**Success Rate**: {summary['success_rate']:.1%}  
**Total Actions**: {summary['total_actions']}  

### Platform Results:
"""

            for result in summary['results']:
                platform = result.get('platform', 'unknown')
                status = result.get('status', 'unknown')
                log_entry += f"- **{platform.title()}**: {status}\n"

            log_entry += f"\n---\n"

            # Append to log file
            if log_file.exists():
                existing_content = log_file.read_text()
                log_file.write_text(log_entry + existing_content)
            else:
                log_file.write_text(f"# SocialFlow AI - Execution Log\n{log_entry}")

            self.logger.info("Execution log saved")

        except Exception as e:
            self.logger.error(f"Failed to save execution log: {e}")

    async def archive_completed_queues(self):
        """Move completed queue files to archive"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            archive_dir = Path("archive")
            archive_dir.mkdir(exist_ok=True)

            for queue_file in Path("content_queue").glob("*.json"):
                if queue_file.stat().st_size > 50:  # If not empty template
                    # Move to archive
                    archive_path = archive_dir / f"{queue_file.stem}_{timestamp}.json"
                    queue_file.rename(archive_path)

                    # Reset to empty template
                    queue_file.write_text('{"execution_status": "pending"}')

            self.logger.info("Queues archived successfully")

        except Exception as e:
            self.logger.error(f"Failed to archive queues: {e}")

    async def cleanup_resources(self):
        """Clean up platform resources"""
        try:
            if hasattr(self.telegram, 'client') and self.telegram.client:
                await self.telegram.disconnect()

            if hasattr(self.threads, 'browser') and self.threads.browser:
                await self.threads.cleanup()

            self.logger.info("Resources cleaned up")

        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

# CLI interface
if __name__ == "__main__":
    import sys

    async def main():
        executor = MasterExecutor()

        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            print("🧪 Running test mode...")
            # Test mode - just verify authentication
            for platform in [executor.reddit, executor.telegram, executor.instagram]:
                try:
                    result = await platform.authenticate()
                    print(f"✅ {platform.name}: {'OK' if result else 'FAILED'}")
                except Exception as e:
                    print(f"❌ {platform.name}: {e}")
        else:
            # Full execution
            result = await executor.execute_daily_batch()
            print(f"Execution completed with {result.get('success_rate', 0):.1%} success rate")

    asyncio.run(main())
