#!/usr/bin/env python3
"""
Fast platform testing for SocialFlow AI
Shows actual posting results on each platform
"""

import asyncio
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv("config/accounts.env")

# Add to path
sys.path.append(str(Path(__file__).parent))

from backend.utils.logger import get_logger
from platforms.reddit_executor import RedditExecutor
from platforms.telegram_executor import TelegramExecutor  
from platforms.threads_executor import ThreadsExecutor
from platforms.instagram_executor import InstagramExecutor

log = get_logger("PlatformTest")

async def test_reddit():
    """Test Reddit posting"""
    print("🧪 Testing REDDIT...")
    
    try:
        # Load queue content
        with open("content_queue/reddit_queue.json", 'r') as f:
            queue_data = json.load(f)
        
        if not queue_data.get("reddit_posts"):
            return {"status": "error", "message": "No Reddit posts in queue"}
        
        post_data = queue_data["reddit_posts"][0]
        
        # Initialize executor
        reddit_exec = RedditExecutor()
        
        # Test posting
        result = await reddit_exec.post_content(post_data)
        
        return {
            "platform": "reddit",
            "attempted": {
                "subreddit": post_data["subreddit"],
                "title": post_data["title"],
                "content_preview": post_data["content"][:100] + "..."
            },
            "result": result,
            "success": result.get("status") == "success",
            "post_url": result.get("post_url", "N/A"),
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "platform": "reddit",
            "error": str(e),
            "success": False
        }

async def test_telegram():
    """Test Telegram messaging"""
    print("🧪 Testing TELEGRAM...")
    
    try:
        # Load queue content
        with open("content_queue/telegram_queue.json", 'r') as f:
            queue_data = json.load(f)
        
        if not queue_data.get("telegram_messages"):
            return {"status": "error", "message": "No Telegram messages in queue"}
        
        message_data = queue_data["telegram_messages"][0]
        
        # Initialize executor
        telegram_exec = TelegramExecutor()
        
        # Test messaging
        result = await telegram_exec.post_content(message_data)
        
        return {
            "platform": "telegram",
            "attempted": {
                "target_groups": message_data["target_groups"],
                "content_preview": message_data["content"][:100] + "..."
            },
            "result": result,
            "success": result.get("status") == "success",
            "message_links": [r.get("message_link") for r in result.get("results", []) if "message_link" in r],
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "platform": "telegram",
            "error": str(e),
            "success": False
        }

async def test_threads():
    """Test Threads posting"""
    print("🧪 Testing THREADS...")
    
    try:
        # Load queue content
        with open("content_queue/threads_queue.json", 'r') as f:
            queue_data = json.load(f)
        
        if not queue_data.get("threads_posts"):
            return {"status": "error", "message": "No Threads posts in queue"}
        
        post_data = queue_data["threads_posts"][0]
        
        # Initialize executor
        threads_exec = ThreadsExecutor()
        
        # Test posting
        result = await threads_exec.post_content(post_data)
        
        return {
            "platform": "threads",
            "attempted": {
                "content_preview": post_data["content"][:100] + "...",
                "hashtags": post_data.get("hashtags", [])
            },
            "result": result,
            "success": result.get("status") == "success",
            "post_url": result.get("post_url", "N/A"),
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "platform": "threads",
            "error": str(e),
            "success": False
        }

async def test_instagram():
    """Test Instagram commenting"""
    print("🧪 Testing INSTAGRAM...")
    
    try:
        # Load queue content
        with open("content_queue/instagram_queue.json", 'r') as f:
            queue_data = json.load(f)
        
        if not queue_data.get("instagram_targets"):
            return {"status": "error", "message": "No Instagram targets in queue"}
        
        target_data = queue_data["instagram_targets"][0]
        
        # Initialize executor
        instagram_exec = InstagramExecutor()
        
        # Test commenting
        result = await instagram_exec.engage_with_content(target_data)
        
        return {
            "platform": "instagram",
            "attempted": {
                "target_account": target_data["account"],
                "keyword": target_data["recent_post_keyword"],
                "comment_preview": target_data["comment"][:100] + "..."
            },
            "result": result,
            "success": result.get("status") == "success",
            "comment_urls": result.get("comment_urls", []),
            "error": result.get("error")
        }
        
    except Exception as e:
        return {
            "platform": "instagram",
            "error": str(e),
            "success": False
        }

async def main():
    """Run all platform tests"""
    print("🚀 SocialFlow AI Platform Tests")
    print("=" * 50)
    
    # Run tests
    results = {}
    
    # Test each platform
    results["reddit"] = await test_reddit()
    results["telegram"] = await test_telegram()  
    results["threads"] = await test_threads()
    results["instagram"] = await test_instagram()
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 PLATFORM TEST RESULTS")
    print("=" * 50)
    
    successful = 0
    total = len(results)
    
    for platform, result in results.items():
        success = result.get("success", False)
        if success:
            successful += 1
            
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\n{platform.upper()}: {status}")
        
        # Show what was attempted
        if "attempted" in result:
            attempt = result["attempted"]
            for key, value in attempt.items():
                print(f"  {key}: {value}")
        
        # Show results
        if success:
            if result.get("post_url") and result["post_url"] != "N/A":
                print(f"  📍 URL: {result['post_url']}")
            if result.get("message_links"):
                for link in result["message_links"]:
                    print(f"  📍 Message: {link}")
            if result.get("comment_urls"):
                for url in result["comment_urls"]:
                    print(f"  📍 Comment: {url}")
        else:
            if result.get("error"):
                print(f"  ❌ Error: {result['error']}")
    
    print(f"\n📈 Overall Success Rate: {successful}/{total} ({successful/total:.1%})")
    
    # Save detailed results
    with open("platform_test_results.json", 'w') as f:
        json.dump({
            "summary": {
                "successful_platforms": successful,
                "total_platforms": total,
                "success_rate": successful / total
            },
            "detailed_results": results
        }, f, indent=2)
    
    print("📄 Detailed results saved to platform_test_results.json")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
    # Exit with success if at least one platform worked
    sys.exit(0 if any(r.get("success", False) for r in results.values()) else 1)