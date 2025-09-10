# Automatic content scheduler for SocialFlow AI
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from llm_providers.enhanced_manager import smart_chat, cleanup_llm_resources
from backend.utils.logger import get_logger

log = get_logger("ContentScheduler")

class AutoContentScheduler:
    """Automatically generate content using LLM providers"""

    def __init__(self):
        self.content_prompts = {
            "reddit": self._get_reddit_prompt(),
            "telegram": self._get_telegram_prompt(), 
            "threads": self._get_threads_prompt(),
            "instagram": self._get_instagram_prompt()
        }

    def _get_reddit_prompt(self) -> str:
        return """Generate Reddit content for social media automation. 

Context: I run an AI-powered trading platform and need engaging Reddit posts.

Analyze current trends in:
- AI and machine learning
- Trading and algorithmic trading  
- Cryptocurrency markets
- Automation and productivity

Generate EXACTLY this JSON format (no other text):

{
  "reddit_posts": [
    {
      "subreddit": "algotrading",
      "title": "Practical trading automation insight",
      "content": "Detailed post with value (300+ words)",
      "timing": "morning_peak",
      "expected_engagement": "high"
    },
    {
      "subreddit": "artificial", 
      "title": "AI discussion topic",
      "content": "Technical but accessible content",
      "timing": "afternoon", 
      "expected_engagement": "medium"
    },
    {
      "subreddit": "programming",
      "title": "Development insight",
      "content": "Code-focused content with examples",
      "timing": "evening",
      "expected_engagement": "high"
    }
  ]
}

Focus on VALUE-FIRST content, never promotional. Make it genuinely helpful."""

    def _get_telegram_prompt(self) -> str:
        return """Generate Telegram content for trading/AI groups.

I need messages for active participation in Telegram groups focused on:
- Trading algorithms
- Python automation
- AI and machine learning
- Cryptocurrency analysis

Generate EXACTLY this JSON format:

{
  "telegram_messages": [
    {
      "target_groups": ["@trading_algorithms", "@python_trading", "@ai_automation"],
      "content": "Valuable insight with actionable information (100-200 words)",
      "timing": "evening",
      "include_media": false
    },
    {
      "target_groups": ["@crypto_signals", "@algorithmic_trading"],
      "content": "Market analysis or technical insight",
      "timing": "morning",
      "include_media": false
    }
  ]
}

Make content conversational but informative. Include relevant emojis sparingly."""

    def _get_threads_prompt(self) -> str:
        return """Generate Threads content for maximum engagement.

I need viral-potential content about:
- AI trends and breakthroughs
- Trading insights and market analysis
- Automation and productivity hacks
- Technology and innovation

Generate EXACTLY this JSON format:

{
  "threads_posts": [
    {
      "content": "Hook-heavy thread starter with trending angle",
      "hashtags": ["#AI", "#Trading", "#Automation"],
      "timing": "peak_hours",
      "thread_length": "single"
    },
    {
      "content": "Engaging question or insight about current trends",
      "hashtags": ["#TechTrends", "#FinTech", "#Innovation"],
      "timing": "afternoon",
      "thread_length": "single"
    }
  ]
}

Focus on engagement bait that provides real value. Use 3-5 trending hashtags."""

    def _get_instagram_prompt(self) -> str:
        return """Generate Instagram engagement strategy for viral posts.

I need strategic comments for viral posts from accounts like:
- @naval (business/philosophy)
- @elonmusk (tech/innovation)
- @garyvee (entrepreneurship)
- @lexfridman (AI/tech)
- Major trading/finance influencers

Generate EXACTLY this JSON format:

{
  "instagram_targets": [
    {
      "account": "@naval",
      "recent_post_keyword": "automation",
      "comment": "Thoughtful value-adding comment that gets attention",
      "timing": "within_2_hours"
    },
    {
      "account": "@elonmusk",
      "recent_post_keyword": "AI",
      "comment": "Technical insight that demonstrates expertise",
      "timing": "within_4_hours"
    },
    {
      "account": "@garyvee",
      "recent_post_keyword": "business",
      "comment": "Practical business automation insight",
      "timing": "within_6_hours"
    },
    {
      "account": "@lexfridman",
      "recent_post_keyword": "technology",
      "comment": "Deep technical perspective on AI/automation",
      "timing": "within_2_hours"
    }
  ]
}

Comments should be VALUABLE, not promotional. Show expertise and insight."""

    async def generate_daily_content(self) -> Dict[str, Any]:
        """Generate complete daily content for all platforms"""
        log.info("🤖 Starting automatic content generation...")

        generated_content = {}
        generation_errors = []

        for platform, prompt in self.content_prompts.items():
            try:
                log.info(f"Generating {platform} content...")

                # Use enhanced LLM manager with fallback
                messages = [
                    {"role": "system", "content": "You are a social media content expert. Return only valid JSON, no other text."},
                    {"role": "user", "content": prompt}
                ]

                response = await smart_chat(messages, max_tokens=1000, temperature=0.7)

                # Parse JSON response
                try:
                    content_json = json.loads(response)
                    generated_content[platform] = content_json
                    log.info(f"✅ {platform} content generated successfully")
                except json.JSONDecodeError as e:
                    log.error(f"❌ {platform} JSON parse failed: {e}")
                    log.error(f"Raw response: {response[:200]}...")

                    # Try to extract JSON from response
                    cleaned_response = self._extract_json_from_response(response)
                    if cleaned_response:
                        generated_content[platform] = cleaned_response
                        log.info(f"✅ {platform} content recovered from response")
                    else:
                        generation_errors.append(f"{platform}: JSON parse failed")

                # Rate limiting delay
                await asyncio.sleep(2)

            except Exception as e:
                log.error(f"❌ {platform} generation failed: {e}")
                generation_errors.append(f"{platform}: {str(e)}")

        result = {
            "generation_time": datetime.now().isoformat(),
            "platforms_generated": len(generated_content),
            "total_platforms": len(self.content_prompts),
            "success_rate": len(generated_content) / len(self.content_prompts),
            "content": generated_content,
            "errors": generation_errors
        }

        log.info(f"🎯 Content generation complete: {result['success_rate']:.1%} success rate")
        return result

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Try to extract JSON from a messy response"""
        try:
            # Look for JSON between ```json and ``` or { and }
            import re

            # Try to find JSON block
            json_match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'({.*})', response, re.DOTALL)

            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)

            return None

        except Exception:
            return None

    async def save_content_to_queues(self, content: Dict[str, Any]):
        """Save generated content to queue files"""
        queue_dir = Path("content_queue")
        queue_dir.mkdir(exist_ok=True)

        platform_mapping = {
            "reddit": "reddit_queue.json",
            "telegram": "telegram_queue.json", 
            "threads": "threads_queue.json",
            "instagram": "instagram_queue.json"
        }

        for platform, queue_file in platform_mapping.items():
            if platform in content["content"]:
                try:
                    platform_content = content["content"][platform]
                    platform_content["execution_status"] = "pending"
                    platform_content["generated_at"] = content["generation_time"]
                    platform_content["auto_generated"] = True

                    queue_path = queue_dir / queue_file
                    with open(queue_path, 'w') as f:
                        json.dump(platform_content, f, indent=2)

                    log.info(f"✅ {platform} content saved to {queue_file}")

                except Exception as e:
                    log.error(f"❌ Failed to save {platform} content: {e}")

    async def run_daily_generation(self):
        """Run complete daily content generation cycle"""
        try:
            # Generate content
            content = await self.generate_daily_content()

            # Save to queue files
            await self.save_content_to_queues(content)

            # Log summary
            log.info(f"📊 Daily generation summary:")
            log.info(f"  - Platforms: {content['platforms_generated']}/{content['total_platforms']}")
            log.info(f"  - Success rate: {content['success_rate']:.1%}")

            if content["errors"]:
                log.warning(f"  - Errors: {content['errors']}")

            return content

        except Exception as e:
            log.error(f"❌ Daily generation failed: {e}")
            raise
        finally:
            # Cleanup resources
            await cleanup_llm_resources()

# CLI interface
async def main():
    """Run content generation from command line"""
    import sys

    scheduler = AutoContentScheduler()

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Testing LLM providers...")
        from llm_providers.enhanced_manager import get_llm_status
        status = await get_llm_status()
        print(f"Available providers: {status['total_providers']}")
        for provider in status['provider_details']:
            print(f"  - {provider['name']}: {'✅' if provider['available'] else '❌'}")
        return

    # Run daily generation
    await scheduler.run_daily_generation()

if __name__ == "__main__":
    asyncio.run(main())
