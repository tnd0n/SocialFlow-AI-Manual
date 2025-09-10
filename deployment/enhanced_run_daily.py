#!/usr/bin/env python3
"""
Enhanced Daily Runner for SocialFlow AI
Automatically generates content and executes across all platforms
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.content_scheduler import AutoContentScheduler
from executors.master_executor import MasterExecutor
from llm_providers.enhanced_manager import get_llm_status, cleanup_llm_resources
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_daily_execution.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedDailyRunner:
    """Enhanced runner with automatic content generation"""

    def __init__(self):
        self.content_scheduler = AutoContentScheduler()
        self.master_executor = MasterExecutor()

    async def check_llm_providers(self) -> bool:
        """Check if LLM providers are available"""
        try:
            status = await get_llm_status()
            available_providers = len([p for p in status['provider_details'] if p['available']])
            total_providers = status['total_providers']

            logger.info(f"LLM Status: {available_providers}/{total_providers} providers available")

            if available_providers == 0:
                logger.error("No LLM providers available - cannot generate content")
                return False

            # Log provider details
            for provider in status['provider_details']:
                status_icon = "✅" if provider['available'] else "❌"
                logger.info(f"  {status_icon} {provider['name']} ({provider['type']})")

            return True

        except Exception as e:
            logger.error(f"Failed to check LLM providers: {e}")
            return False

    async def generate_content(self) -> bool:
        """Generate content for all platforms"""
        try:
            logger.info("🤖 Starting automatic content generation...")

            # Generate content using LLM providers
            result = await self.content_scheduler.run_daily_generation()

            success_rate = result.get('success_rate', 0)
            platforms_generated = result.get('platforms_generated', 0)

            if success_rate >= 0.5:  # At least 50% success
                logger.info(f"✅ Content generation successful: {platforms_generated} platforms, {success_rate:.1%} success rate")
                return True
            else:
                logger.warning(f"⚠️ Content generation partially failed: {success_rate:.1%} success rate")
                return platforms_generated > 0  # Continue if we got at least some content

        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            return False

    async def execute_social_media(self) -> bool:
        """Execute social media posting"""
        try:
            logger.info("📱 Starting social media execution...")

            # Execute across all platforms
            result = await self.master_executor.execute_daily_batch()

            success_rate = result.get('success_rate', 0)
            total_actions = result.get('total_actions', 0)

            if success_rate >= 0.6:  # At least 60% success
                logger.info(f"✅ Social media execution successful: {success_rate:.1%} success rate ({total_actions} actions)")
                return True
            else:
                logger.warning(f"⚠️ Social media execution had issues: {success_rate:.1%} success rate")
                return True  # Continue even with low success rate

        except Exception as e:
            logger.error(f"❌ Social media execution failed: {e}")
            return False

    async def run_full_cycle(self) -> int:
        """Run complete daily cycle: generate → execute → report"""
        start_time = datetime.now()
        logger.info("🚀 Starting enhanced SocialFlow AI daily cycle")

        try:
            # Step 1: Check LLM providers
            if not await self.check_llm_providers():
                logger.error("Cannot proceed without LLM providers")
                return 1

            # Step 2: Generate content automatically
            content_success = await self.generate_content()

            # Step 3: Execute social media posting (even if content generation partial)
            execution_success = await self.execute_social_media()

            # Step 4: Generate summary
            duration = (datetime.now() - start_time).total_seconds() / 60

            logger.info("📊 Daily cycle summary:")
            logger.info(f"  - Duration: {duration:.1f} minutes")
            logger.info(f"  - Content generation: {'✅' if content_success else '❌'}")
            logger.info(f"  - Social media execution: {'✅' if execution_success else '❌'}")

            # Determine exit code
            if content_success and execution_success:
                logger.info("🎉 Daily cycle completed successfully!")
                return 0
            elif execution_success:
                logger.warning("⚠️ Daily cycle completed with content generation issues")
                return 2
            else:
                logger.error("❌ Daily cycle failed")
                return 1

        except Exception as e:
            logger.error(f"💥 Daily cycle crashed: {e}")
            return 1
        finally:
            # Cleanup resources
            await cleanup_llm_resources()

async def main():
    """Main execution function"""
    # Load environment variables
    env_path = Path("config/accounts.env")
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Environment variables loaded")
    else:
        logger.error("accounts.env not found - copy from template and fill values")
        return 1

    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-llm":
            # Test LLM providers only
            runner = EnhancedDailyRunner()
            success = await runner.check_llm_providers()
            return 0 if success else 1

        elif sys.argv[1] == "--generate-only":
            # Generate content only
            runner = EnhancedDailyRunner()
            success = await runner.generate_content()
            return 0 if success else 1

        elif sys.argv[1] == "--execute-only":
            # Execute existing content only
            runner = EnhancedDailyRunner()
            success = await runner.execute_social_media()
            return 0 if success else 1

        elif sys.argv[1] == "--help":
            print("""
Enhanced SocialFlow AI Daily Runner

Usage:
  python deployment/enhanced_run_daily.py           # Full cycle (generate + execute)
  python deployment/enhanced_run_daily.py --test-llm     # Test LLM providers
  python deployment/enhanced_run_daily.py --generate-only # Generate content only
  python deployment/enhanced_run_daily.py --execute-only  # Execute existing content
  python deployment/enhanced_run_daily.py --help         # Show this help
            """)
            return 0

    # Run full cycle
    runner = EnhancedDailyRunner()
    return await runner.run_full_cycle()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
