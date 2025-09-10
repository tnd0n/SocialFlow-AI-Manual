# SocialFlow AI - Deployment Guide

## 🚀 Quick Setup (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/tnd0n/SocialFlow-AI-Manual.git
cd SocialFlow-AI-Manual
chmod +x setup.sh
./setup.sh
```

### 2. Configure Credentials  
```bash
# Edit with your actual API keys
nano config/accounts.env
```

### 3. Test Authentication
```bash
python executors/master_executor.py --test
```

### 4. Generate Content with Perplexity
Use the prompt from `docs/perplexity_integration.md` to generate daily content.

### 5. Execute
```bash
# Manual execution
python deployment/run_daily.py

# Or let cron handle it (runs daily at 10 AM)
```

## 📊 Monitoring

### Check Health
```bash
python deployment/monitor.py
```

### View Execution Log
```bash
cat EXECUTION_LOG.md
```

### Check Recent Activity  
```bash
tail -f daily_execution.log
```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Plain Docker
```bash
# Build image
docker build -t socialflow-ai .

# Run container
docker run -d \
  --name socialflow-ai \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/content_queue:/app/content_queue \
  -v $(pwd)/logs:/app/logs \
  socialflow-ai
```

## 📁 File Structure Overview

```
SocialFlow-AI-Manual/
├── config/                 # Configuration files
├── content_queue/          # JSON files with content to post
├── platforms/              # Platform-specific executors  
├── executors/              # Main execution logic
├── deployment/             # Scripts for running and monitoring
├── docs/                   # Documentation and guides
├── accounts/               # Session files and cookies (gitignored)
├── archive/                # Completed content batches
└── logs/                   # Execution and health logs
```

## ⚡ Daily Workflow

1. **Morning**: Ask Perplexity for trend analysis and content generation
2. **Copy**: Paste JSON responses to `content_queue/*.json` files  
3. **Commit**: `git add content_queue/ && git commit -m "Daily batch" && git push`
4. **Execute**: Automatic via cron or manual via `python deployment/run_daily.py`
5. **Monitor**: Check `EXECUTION_LOG.md` for results

## 🔒 Security Features

- ✅ API keys stored in gitignored `.env` files
- ✅ Session cookies encrypted and cached
- ✅ Rate limiting to avoid platform restrictions
- ✅ Human-like delays between actions
- ✅ Account health monitoring
- ✅ Automatic error recovery

## 📈 Performance Metrics

Track success via:
- **Execution logs**: Success rates by platform
- **Health monitoring**: Account status and restrictions
- **Engagement metrics**: Comments, likes, follows gained
- **Content performance**: Which posts get best engagement

## 🛠️ Troubleshooting

### Authentication Issues
```bash
# Test each platform
python executors/master_executor.py --test

# Check credentials
cat config/accounts.env | grep -v "^#"
```

### Low Success Rates  
- Check `EXECUTION_LOG.md` for error patterns
- Reduce posting frequency in `config/behavior_settings.py`
- Improve content quality via better Perplexity prompts

### Platform Restrictions
- Run health check: `python deployment/monitor.py`
- Reduce daily limits in configuration
- Take a 1-2 day break for flagged accounts

### Content Not Engaging
- Analyze successful competitors' content
- Ask Perplexity for trending topic analysis
- Focus on value-driven rather than promotional content

## 📞 Support

For issues or improvements:
1. Check existing execution logs first
2. Run health monitoring to identify problems  
3. Review Perplexity integration guide for better content
4. Adjust rate limits and behavior settings as needed

## 🎯 Success Metrics

Target KPIs:
- **Success Rate**: >80% actions complete successfully
- **Account Health**: 0 restrictions or bans
- **Engagement Growth**: Increasing followers/connections  
- **Content Performance**: Higher engagement rates over time
- **Automation Uptime**: 95%+ daily execution success

The system is designed for sustainable, long-term growth while maintaining natural, human-like behavior patterns.
