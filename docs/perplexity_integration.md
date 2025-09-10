# Perplexity Integration Guide for SocialFlow AI

This guide explains how to use Perplexity to generate content for automated social media posting.

## Daily Workflow

### 1. Perplexity Content Generation Prompt

Copy this prompt to Perplexity (customize based on your niche):

```
Hey Perplexity, I need you to analyze current trends and generate social media content for my automation system.

Context: I'm building an AI-powered trading/automation platform and need to engage across Reddit, Telegram, Threads, and Instagram.

Please analyze:
1. Latest trends in AI, trading, automation, and fintech
2. Viral content patterns on each platform
3. Engagement opportunities (trending hashtags, viral posts, active communities)

Generate content in this exact JSON format:

REDDIT POSTS:
{
  "reddit_posts": [
    {
      "subreddit": "algotrading",
      "title": "[Engaging title about trading automation]",
      "content": "[Detailed post content with value and insights]",
      "timing": "morning_peak",
      "expected_engagement": "high"
    },
    {
      "subreddit": "artificial", 
      "title": "[AI discussion topic]",
      "content": "[Technical but accessible AI content]",
      "timing": "afternoon",
      "expected_engagement": "medium"
    }
  ]
}

TELEGRAM MESSAGES:
{
  "telegram_messages": [
    {
      "target_groups": ["@trading_algorithms", "@python_trading"],
      "content": "[Valuable insight with code snippet or analysis]",
      "timing": "evening",
      "include_media": false
    }
  ]
}

THREADS POSTS:
{
  "threads_posts": [
    {
      "content": "[Engaging thread starter with trending hooks]",
      "hashtags": ["#AI", "#Trading", "#Automation"],
      "timing": "peak_hours",
      "thread_length": "single"
    }
  ]
}

INSTAGRAM TARGETS:
{
  "instagram_targets": [
    {
      "account": "@naval",
      "recent_post_keyword": "automation",
      "comment": "[Value-adding comment that gets attention]",
      "timing": "within_2_hours"
    },
    {
      "account": "@elonmusk", 
      "recent_post_keyword": "AI",
      "comment": "[Insightful technical comment]",
      "timing": "within_4_hours"
    }
  ]
}

Focus on:
- Trending topics in AI/trading/automation
- Value-driven content (not promotional)
- Platform-specific optimization
- Current viral patterns and hashtags
```

### 2. Copy JSON Responses

After Perplexity responds, copy each JSON section to the respective queue files:

- **Reddit JSON** → `content_queue/reddit_queue.json`
- **Telegram JSON** → `content_queue/telegram_queue.json`  
- **Threads JSON** → `content_queue/threads_queue.json`
- **Instagram JSON** → `content_queue/instagram_queue.json`

### 3. Commit and Push

```bash
git add content_queue/
git commit -m "Daily content batch $(date +%Y%m%d)"
git push origin main
```

### 4. Execute (Automatic or Manual)

The system will execute automatically via cron, or run manually:
```bash
python deployment/run_daily.py
```

## Advanced Prompts

### Trend Analysis Prompt
```
Perplexity, analyze the top 10 trending topics in:
- r/algotrading (Reddit)
- AI Twitter/X accounts
- #TradingView hashtag on Instagram
- Telegram crypto/trading channels

Identify content opportunities and suggest specific engagement strategies for each platform.
```

### Competitive Analysis Prompt
```
Analyze successful social media accounts in AI/trading space:
- What content gets the most engagement?
- What posting times are optimal?
- Which hashtags are trending?
- What conversation topics are hot right now?

Generate content that joins these conversations authentically.
```

### Weekly Strategy Prompt
```
Based on market events this week and upcoming economic calendar:
- Monday: Focus on market analysis (Reddit + Telegram)
- Tuesday-Thursday: AI/tech discussions (all platforms)
- Friday: Community engagement (Threads + Instagram)
- Weekend: Educational content

Generate a week's worth of content following this strategy.
```

## Content Quality Guidelines

### Reddit
- **Detailed posts** (300+ words)
- **Provide value** first, promote never
- **Use data and insights** 
- **Match subreddit culture**

### Telegram  
- **Concise but informative** (100-200 words)
- **Include actionable insights**
- **Use relevant emojis sparingly**
- **Avoid spam behavior**

### Threads
- **Hook in first line**
- **Use trending hashtags** (3-5 max)
- **Engage with current events**
- **Visual/thread-worthy content**

### Instagram
- **Value-adding comments** only
- **Relevant to post content**
- **Professional but conversational**
- **No promotional language**

## Monitoring Success

Check `EXECUTION_LOG.md` daily for:
- Success rates by platform
- Engagement metrics
- Failed actions (to improve content)
- Account health status

## Troubleshooting

### Low Engagement
- Ask Perplexity to analyze why content isn't resonating
- Request more trending/viral content angles
- Analyze successful competitors' content

### Platform Restrictions
- Reduce posting frequency
- Improve content quality/originality
- Use more human-like language patterns

### Content Ideas Exhausted
- Use broader trend analysis prompts
- Analyze adjacent industries (fintech, SaaS, productivity)
- Ask for content series/campaigns ideas

This manual approach gives you full control over content quality while maintaining automation benefits.
