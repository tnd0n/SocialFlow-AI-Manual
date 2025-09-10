#!/usr/bin/env python3
"""
Daily execution script for SocialFlow AI
Run this once per day to execute all queued content across platforms
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from executors.master_executor import MasterExecutor
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_execution.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def check_prerequisites():
    """Check if all required files and configs exist"""
    required_files = [
        "config/accounts.env",
        "content_queue/reddit_queue.json",
        "content_queue/telegram_queue.json", 
        "content_queue/threads_queue.json",
        "content_queue/instagram_queue.json"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"Missing required files: {missing_files}")
        return False

    # Check if queues have content
    queue_dir = Path("content_queue")
    has_content = False

    for queue_file in queue_dir.glob("*.json"):
        if queue_file.stat().st_size > 100:  # More than empty template
            has_content = True
            break

    if not has_content:
        logger.warning("No content found in queues - nothing to execute")
        return False

    logger.info("Prerequisites check passed")
    return True

async def main():
    """Main execution function"""
    logger.info("🚀 Starting SocialFlow AI daily execution")

    # Load environment variables
    env_path = Path("config/accounts.env")
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Environment variables loaded")
    else:
        logger.error("accounts.env not found - copy from accounts_template.env and fill values")
        return 1

    # Check prerequisites
    if not await check_prerequisites():
        logger.error("Prerequisites check failed")
        return 1

    # Execute daily batch
    executor = MasterExecutor()

    try:
        result = await executor.execute_daily_batch()

        success_rate = result.get('success_rate', 0)
        total_actions = result.get('total_actions', 0)

        if success_rate >= 0.7:  # 70% success threshold
            logger.info(f"✅ Daily execution completed successfully: {success_rate:.1%} success rate ({total_actions} actions)")
            return 0
        else:
            logger.warning(f"⚠️ Daily execution completed with low success rate: {success_rate:.1%} ({total_actions} actions)")
            return 2

    except Exception as e:
        logger.error(f"❌ Daily execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
