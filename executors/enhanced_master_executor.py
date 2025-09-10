# Enhanced master executor with automatic content generation integration
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
from core.content_scheduler import AutoContentScheduler
from llm_providers.enhanced_manager import cleanup_llm_resources

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_execution.log'),
        logging.StreamHandler()
    ]
)

class EnhancedMasterExecutor:
    """Enhanced executor with automatic content generation and smart execution"""

    def __init__(self):
        self.logger = logging.getLogger("EnhancedMasterExecutor")

        # Initialize platform executors
        self.reddit = RedditExecutor()
        self.telegram = TelegramExecutor()
        self.threads = ThreadsExecutor()
        self.instagram = InstagramExecutor()

        # Initialize content scheduler
        self.content_scheduler = AutoContentScheduler()

        self.execution_log = []
        self.daily_limits = {
            "reddit_posts": int(os.getenv("REDDIT_DAILY_POSTS", "3")),
            "telegram_messages": int(os.getenv("TELEGRAM_DAILY_MESSAGES", "5")),
            "threads_posts": int(os.getenv("THREADS_DAILY_POSTS", "4")),
            "instagram_comments": int(os.getenv("INSTAGRAM_DAILY_COMMENTS", "8")),
            "total_actions": int(os.getenv("MAX_DAILY_ACTIONS", "20"))
        }

    async def should_generate_content(self) -> bool:
        """Check if we should generate new content"""
        queue_dir = Path("content_queue")

        # Check if queue files are empty or old
        for queue_file in ["reddit_queue.json", "telegram_queue.json", "threads_queue.json", "instagram_queue.json"]:
            file_path = queue_dir / queue_file

            if not file_path.exists():
                return True

            try:
                with open(file_path, 'r') as f:
                    content = json.load(f)

                # Check if content is substantial and recent
                if content.get("execution_status") == "pending" and len(str(content)) > 100:
                    # Check if content is less than 24 hours old
                    created_at = content.get("created_at", content.get("generated_at"))
                    if created_at:
                        content_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if (datetime.now() - content_time.replace(tzinfo=None)).hours < 24:
                            continue  # This queue has recent content

                return True  # Found empty or old queue

            except:
                return True  # Problem reading queue, regenerate

        return False  # All queues have recent content

    async def execute_with_content_generation(self) -> Dict[str, Any]:
        """Execute complete cycle with automatic content generation"""
        start_time = datetime.now()
        self.logger.info("🚀 Starting enhanced execution cycle with auto-generation")

        try:
            # Step 1: Check if we need to generate content
            need_content = await self.should_generate_content()
            content_generated = False

            if need_content:
                self.logger.info("📝 Generating fresh content...")
                try:
                    generation_result = await self.content_scheduler.run_daily_generation()
                    content_generated = generation_result.get('success_rate', 0) > 0.3

                    if content_generated:
                        self.logger.info(f"✅ Content generated: {generation_result['success_rate']:.1%} success rate")
                    else:
                        self.logger.warning("⚠️ Content generation had low success rate, proceeding with existing content")

                except Exception as e:
                    self.logger.error(f"❌ Content generation failed: {e}")
                    self.logger.info("📋 Proceeding with existing content in queues")
            else:
                self.logger.info("📋 Using existing content from queues")

            # Step 2: Execute social media posting
            execution_result = await self.execute_social_media_batch()

            # Step 3: Compile results
            duration = (datetime.now() - start_time).total_seconds() / 60

            final_result = {
                "execution_date": start_time.isoformat(),
                "duration_minutes": duration,
                "content_generated": content_generated,
                "social_media_execution": execution_result,
                "overall_success": execution_result.get('success_rate', 0) > 0.5,
                "summary": {
                    "content_generation": "✅ Generated" if content_generated else "📋 Used existing",
                    "platforms_executed": execution_result.get('platforms_executed', 0),
                    "total_actions": execution_result.get('total_actions', 0),
                    "success_rate": execution_result.get('success_rate', 0)
                }
            }

            # Save execution log
            await self.save_enhanced_execution_log(final_result)

            self.logger.info(f"🎉 Enhanced execution complete: {final_result['summary']['success_rate']:.1%} success rate")
            return final_result

        except Exception as e:
            self.logger.error(f"💥 Enhanced execution failed: {e}")
            return {
                "execution_date": start_time.isoformat(),
                "status": "failed",
                "error": str(e),
                "overall_success": False
            }
        finally:
            # Cleanup LLM resources
            await cleanup_llm_resources()

    async def execute_social_media_batch(self) -> Dict[str, Any]:
        """Execute social media posting across all platforms"""
        all_results = []

        try:
            # Execute in optimal time-based order
            platform_schedule = [
                ("reddit", self.execute_reddit_queue),
                ("telegram", self.execute_telegram_queue), 
                ("threads", self.execute_threads_queue),
                ("instagram", self.execute_instagram_queue)
            ]

            for platform_name, executor_func in platform_schedule:
                try:
                    self.logger.info(f"📱 Executing {platform_name} queue...")
                    platform_results = await executor_func()
                    all_results.extend(platform_results)

                    # Dynamic delay based on success rate
                    if platform_results and len(platform_results) > 0:
                        delay = random.randint(300, 900)  # 5-15 minutes
                        self.logger.info(f"⏳ Waiting {delay}s before next platform...")
                        await asyncio.sleep(delay)

                except Exception as e:
                    self.logger.error(f"❌ {platform_name} execution failed: {e}")
                    all_results.append({"platform": platform_name, "status": "error", "error": str(e)})

            # Calculate summary
            success_count = len([r for r in all_results if r.get("status") == "success"])
            total_count = len(all_results)

            return {
                "platforms_executed": len(set(r.get("platform") for r in all_results if r.get("platform"))),
                "total_actions": total_count,
                "successful_actions": success_count,
                "success_rate": success_count / total_count if total_count > 0 else 0,
                "results": all_results
            }

        except Exception as e:
            self.logger.error(f"Social media batch execution failed: {e}")
            return {
                "platforms_executed": 0,
                "total_actions": 0,
                "success_rate": 0,
                "error": str(e)
            }

    # Include the existing execute_*_queue methods from the original master_executor
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
                await asyncio.sleep(delay)

            except Exception as e:
                self.logger.error(f"Reddit post failed: {e}")
                results.append({"status": "error", "error": str(e), "platform": "reddit"})

        return results

    # Add other execute_*_queue methods here (telegram, threads, instagram)
    # ... (keeping methods from original for brevity)

    async def load_content_queue(self, queue_file: str) -> Dict[str, Any]:
        """Load content from queue file"""
        file_path = Path("content_queue") / queue_file

        if not file_path.exists():
            return {}

        try:
            with open(file_path, 'r') as f:
                content = json.load(f)

            if content.get("execution_status") == "completed":
                return {}

            return content

        except Exception as e:
            self.logger.error(f"Failed to load queue {queue_file}: {e}")
            return {}

    async def save_enhanced_execution_log(self, result: Dict[str, Any]):
        """Save enhanced execution results"""
        try:
            log_file = Path("EXECUTION_LOG.md")

            # Create enhanced log entry
            log_entry = f"""
## {result['execution_date'][:10]} - Enhanced Daily Execution

**Duration**: {result['duration_minutes']:.1f} minutes  
**Content Generation**: {result.get('content_generated', 'N/A')}  
**Success Rate**: {result.get('summary', {}).get('success_rate', 0):.1%}  
**Total Actions**: {result.get('summary', {}).get('total_actions', 0)}  
**Platforms**: {result.get('summary', {}).get('platforms_executed', 0)}  

### Execution Summary:
{result.get('summary', {})}

---
"""

            # Append to log file
            if log_file.exists():
                existing_content = log_file.read_text()
                log_file.write_text(log_entry + existing_content)
            else:
                log_file.write_text(f"# SocialFlow AI - Enhanced Execution Log\n{log_entry}")

            self.logger.info("Enhanced execution log saved")

        except Exception as e:
            self.logger.error(f"Failed to save execution log: {e}")

# For backward compatibility
class MasterExecutor(EnhancedMasterExecutor):
    """Backward compatible master executor"""

    async def execute_daily_batch(self):
        """Legacy method that calls enhanced execution"""
        return await self.execute_with_content_generation()
