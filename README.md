# SocialFlow AI - Manual Content Push System

Autonomous social media engagement platform with zero API costs.
Feed content from Perplexity → Auto-distribute across Reddit, Telegram, Threads, Instagram.

## Quick Start

1. **Generate Content**: Ask Perplexity to analyze trends and generate content
2. **Copy to Queues**: Paste JSON responses to `content_queue/` files
3. **Commit & Push**: Git commit triggers auto-execution
4. **Monitor**: Check `EXECUTION_LOG.md` for results

## Workflow
```
Perplexity Analysis → JSON Queues → GitHub → Auto-Executor → Social Platforms
```

## Features
- ✅ Reddit posting (no API limits)
- ✅ Telegram group engagement  
- ✅ Threads hashtag monitoring
- ✅ Instagram viral post commenting
- ✅ Human-like behavior simulation
- ✅ Zero AI API costs (manual feed)

## Platforms Supported
- **Reddit**: API + Web session hybrid
- **Telegram**: Telethon + Bot API
- **Threads**: Web automation 
- **Instagram**: Instagrapi library

## Daily Routine (5 minutes)
1. Tell Perplexity: "Analyze my SocialFlow repo and generate today's content batch"
2. Copy JSON responses to queue files
3. `git add content_queue/ && git commit -m "Daily batch" && git push`
4. Automation handles the rest

## Safety Features
- Rate limiting (max 50 actions/day)
- Human-like delays (30s-30min between actions)
- Account health monitoring
- Geo-consistent IP usage
- Weekly rest periods

Built for sustainable, undetectable social media growth.
