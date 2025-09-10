#!/usr/bin/env python3
"""
Testing configuration for SocialFlow AI
Disables delays and enables fast testing mode
"""

import os
import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Set test mode environment variable
os.environ['SOCIALFLOW_TEST_MODE'] = 'true'

from dotenv import load_dotenv
from backend.utils.logger import get_logger
from executors.master_executor import MasterExecutor

log = get_logger("TestRunner")

class PlatformTestRunner:
    """Fast platform testing with no delays"""
    
    def __init__(self):
        self.load_environment()
        
    def load_environment(self):
        """Load environment variables"""
        env_path = Path("config/accounts.env")
        if env_path.exists():
            load_dotenv(env_path)
            log.info("✅ Test environment loaded")
        else:
            log.error("❌ accounts.env not found")
    
    async def test_platform_individually(self, platform: str):
        """Test a single platform without delays"""
        log.info(f"🧪 Testing {platform.upper()} platform...")
        
        try:
            executor = MasterExecutor()
            
            # Override delays for testing
            original_get_delay = hasattr(executor, 'get_realistic_delay')
            if original_get_delay:
                executor.get_realistic_delay = lambda action_type: 1  # 1 second delay
            
            # Test specific platform
            if platform == "reddit":
                result = await self.test_reddit_posting(executor)
            elif platform == "telegram":
                result = await self.test_telegram_posting(executor)
            elif platform == "threads":
                result = await self.test_threads_posting(executor)
            elif platform == "instagram":
                result = await self.test_instagram_posting(executor)
            else:
                return {"status": "error", "message": f"Unknown platform: {platform}"}
            
            return result
            
        except Exception as e:
            log.error(f"❌ {platform} test failed: {e}")
            return {
                "status": "error",
                "platform": platform,
                "error": str(e),
                "posted": False
            }
    
    async def test_reddit_posting(self, executor):
        """Test Reddit posting with immediate results"""
        try:
            from platforms.reddit_executor import RedditExecutor
            reddit_exec = RedditExecutor()
            
            # Test content from queue
            queue_path = Path("content_queue/reddit_queue.json")
            if not queue_path.exists():
                return {"status": "error", "message": "Reddit queue not found"}
            
            import json
            with open(queue_path, 'r') as f:
                queue_data = json.load(f)
            
            if not queue_data.get("reddit_posts"):
                return {"status": "error", "message": "No Reddit posts in queue"}
            
            post_data = queue_data["reddit_posts"][0]
            
            # Attempt to post (this will show authentication status)
            result = await reddit_exec.post_content(
                subreddit=post_data["subreddit"],
                title=post_data["title"],
                content=post_data["content"]
            )
            
            return {
                "status": "tested",
                "platform": "reddit",
                "attempted_post": {
                    "subreddit": post_data["subreddit"],
                    "title": post_data["title"],
                    "content": post_data["content"][:100] + "..."
                },
                "result": result,
                "posted": result.get("status") == "success",
                "post_url": result.get("post_url", "N/A"),
                "error": result.get("error")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "platform": "reddit", 
                "error": str(e),
                "posted": False
            }
    
    async def test_telegram_posting(self, executor):
        """Test Telegram posting"""
        try:
            from platforms.telegram_executor import TelegramExecutor
            telegram_exec = TelegramExecutor()
            
            queue_path = Path("content_queue/telegram_queue.json")
            if not queue_path.exists():
                return {"status": "error", "message": "Telegram queue not found"}
            
            import json
            with open(queue_path, 'r') as f:
                queue_data = json.load(f)
            
            if not queue_data.get("telegram_messages"):
                return {"status": "error", "message": "No Telegram messages in queue"}
            
            message_data = queue_data["telegram_messages"][0]
            
            # Test sending message
            result = await telegram_exec.send_message(
                target_groups=message_data["target_groups"],
                content=message_data["content"]
            )
            
            return {
                "status": "tested",
                "platform": "telegram",
                "attempted_post": {
                    "groups": message_data["target_groups"],
                    "content": message_data["content"][:100] + "..."
                },
                "result": result,
                "posted": result.get("status") == "success",
                "message_ids": result.get("message_ids", []),
                "error": result.get("error")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "platform": "telegram",
                "error": str(e),
                "posted": False
            }
    
    async def test_threads_posting(self, executor):
        """Test Threads posting"""
        try:
            from platforms.threads_executor import ThreadsExecutor
            threads_exec = ThreadsExecutor()
            
            queue_path = Path("content_queue/threads_queue.json")
            if not queue_path.exists():
                return {"status": "error", "message": "Threads queue not found"}
            
            import json
            with open(queue_path, 'r') as f:
                queue_data = json.load(f)
            
            if not queue_data.get("threads_posts"):
                return {"status": "error", "message": "No Threads posts in queue"}
            
            post_data = queue_data["threads_posts"][0]
            
            # Test posting
            result = await threads_exec.post_content(
                content=post_data["content"],
                hashtags=post_data.get("hashtags", [])
            )
            
            return {
                "status": "tested",
                "platform": "threads",
                "attempted_post": {
                    "content": post_data["content"][:100] + "...",
                    "hashtags": post_data.get("hashtags", [])
                },
                "result": result,
                "posted": result.get("status") == "success",
                "post_url": result.get("post_url", "N/A"),
                "error": result.get("error")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "platform": "threads",
                "error": str(e),
                "posted": False
            }
    
    async def test_instagram_posting(self, executor):
        """Test Instagram commenting"""
        try:
            from platforms.instagram_executor import InstagramExecutor
            instagram_exec = InstagramExecutor()
            
            queue_path = Path("content_queue/instagram_queue.json")
            if not queue_path.exists():
                return {"status": "error", "message": "Instagram queue not found"}
            
            import json
            with open(queue_path, 'r') as f:
                queue_data = json.load(f)
            
            if not queue_data.get("instagram_targets"):
                return {"status": "error", "message": "No Instagram targets in queue"}
            
            target_data = queue_data["instagram_targets"][0]
            
            # Test commenting
            result = await instagram_exec.comment_on_posts(
                target_account=target_data["account"],
                keyword=target_data["recent_post_keyword"],
                comment=target_data["comment"]
            )
            
            return {
                "status": "tested",
                "platform": "instagram",
                "attempted_action": {
                    "account": target_data["account"],
                    "keyword": target_data["recent_post_keyword"],
                    "comment": target_data["comment"][:100] + "..."
                },
                "result": result,
                "posted": result.get("status") == "success",
                "comment_urls": result.get("comment_urls", []),
                "error": result.get("error")
            }
            
        except Exception as e:
            return {
                "status": "error",
                "platform": "instagram",
                "error": str(e),
                "posted": False
            }
    
    async def run_all_platform_tests(self):
        """Run tests on all platforms and generate report"""
        print("🚀 Starting Fast Platform Tests (No Delays)")
        print("=" * 60)
        
        platforms = ["reddit", "telegram", "threads", "instagram"]
        results = {}
        
        for platform in platforms:
            print(f"\n🧪 Testing {platform.upper()}...")
            result = await self.test_platform_individually(platform)
            results[platform] = result
            
            # Print immediate results
            if result["status"] == "tested":
                status_emoji = "✅" if result["posted"] else "❌"
                print(f"  {status_emoji} {platform.upper()}: {'POSTED' if result['posted'] else 'FAILED'}")
                if result.get("error"):
                    print(f"    Error: {result['error']}")
                if result.get("post_url") and result["post_url"] != "N/A":
                    print(f"    URL: {result['post_url']}")
            else:
                print(f"  ❌ {platform.upper()}: ERROR - {result.get('error', 'Unknown error')}")
        
        # Generate summary report
        print("\n" + "=" * 60)
        print("📊 PLATFORM TEST SUMMARY")
        print("=" * 60)
        
        successful_posts = 0
        total_platforms = len(platforms)
        
        for platform, result in results.items():
            posted = result.get("posted", False)
            if posted:
                successful_posts += 1
            
            status = "✅ POSTED" if posted else "❌ FAILED" 
            print(f"{platform.upper():12} | {status}")
            
            if result.get("attempted_post"):
                attempt = result["attempted_post"]
                if "title" in attempt:
                    print(f"             | Title: {attempt['title']}")
                elif "content" in attempt:
                    print(f"             | Content: {attempt['content']}")
                elif "groups" in attempt:
                    print(f"             | Groups: {', '.join(attempt['groups'])}")
            
            if result.get("error"):
                print(f"             | Error: {result['error']}")
        
        success_rate = successful_posts / total_platforms
        print(f"\n📈 Success Rate: {successful_posts}/{total_platforms} ({success_rate:.1%})")
        
        # Save detailed results
        import json
        results_file = Path("platform_test_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": log.root.handlers[0].formatter.formatTime(log.root.makeRecord("", 0, "", 0, "", (), None)),
                "summary": {
                    "successful_posts": successful_posts,
                    "total_platforms": total_platforms,
                    "success_rate": success_rate
                },
                "platform_results": results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")
        
        return results

async def main():
    """Main test runner"""
    runner = PlatformTestRunner()
    results = await runner.run_all_platform_tests()
    
    # Exit with status based on results  
    successful = sum(1 for r in results.values() if r.get("posted", False))
    return 0 if successful > 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)