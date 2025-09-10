# SocialFlow AI Enhanced - Complete Deployment Guide

## 🚀 Zero-Cost Automated Social Media System

This guide covers deploying the enhanced SocialFlow AI system with **completely free** content generation using web-based LLM providers.

## 📋 Prerequisites

- Python 3.11+
- Git
- Chrome/Chromium browser
- 15 minutes for initial setup

## 🛠️ Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/tnd0n/SocialFlow-AI-Manual.git
cd SocialFlow-AI-Manual
```

### Step 2: Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Make scripts executable
chmod +x setup_cookies.py
chmod +x deployment/enhanced_run_daily.py
```

### Step 3: Setup Web Provider Authentication
```bash
python setup_cookies.py
```

This interactive script will:
1. Open browser windows for Perplexity, ChatGPT, and Gemini
2. Guide you through logging into each service
3. Save authentication cookies for automated access
4. Test the connections to ensure they work

**Important**: Use your actual accounts for these services (free accounts work perfectly).

### Step 4: Configure Social Media Credentials
```bash
cp config/accounts_enhanced_template.env config/accounts.env
nano config/accounts.env  # or use your preferred editor
```

Fill in your social media credentials:
- Reddit API keys and login
- Telegram bot token and API credentials  
- Instagram login
- (Optional) Any paid LLM API keys for extra reliability

### Step 5: Test the System
```bash
# Test LLM providers
python deployment/enhanced_run_daily.py --test-llm

# Test content generation
python deployment/enhanced_run_daily.py --generate-only

# Test social media posting
python deployment/enhanced_run_daily.py --execute-only
```

Each test should show ✅ success indicators.

## ⚙️ Automation Setup

### Option A: Cron Job (Recommended)
```bash
# Edit crontab
crontab -e

# Add this line for daily execution at 8 AM
0 8 * * * cd /path/to/SocialFlow-AI-Manual && python deployment/enhanced_run_daily.py >> logs/cron.log 2>&1
```

### Option B: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f socialflow-ai
```

### Option C: Manual Daily Execution
```bash
# Run complete cycle
python deployment/enhanced_run_daily.py
```

## 🔧 Configuration Options

### Provider Priority
Edit `config/accounts.env`:
```bash
# Order of providers to try (first to last)
LLM_PROVIDER_PRIORITY=perplexity_web,chatgpt_web,gemini_web,openai,perplexity,gemini
```

### Content Quality Settings
```bash
# Enable content validation
ENABLE_CONTENT_VALIDATION=true

# Content length limits
MIN_CONTENT_LENGTH=100
MAX_CONTENT_LENGTH=2000

# Daily limits
MAX_DAILY_LLM_CALLS=50
MAX_HOURLY_LLM_CALLS=10
```

### Platform-Specific Limits
```bash
# Daily posting limits per platform
REDDIT_DAILY_POSTS=3
TELEGRAM_DAILY_MESSAGES=5
THREADS_DAILY_POSTS=4
INSTAGRAM_DAILY_COMMENTS=8
```

## 📊 Monitoring & Maintenance

### Daily Health Checks
```bash
# Check system health
python deployment/monitor.py

# View execution logs
tail -f enhanced_daily_execution.log

# Check LLM provider status
python deployment/enhanced_run_daily.py --test-llm
```

### Weekly Maintenance
1. **Cookie Refresh**: Re-run `python setup_cookies.py` if web providers start failing
2. **Log Cleanup**: Archive old log files
3. **Performance Review**: Check `EXECUTION_LOG.md` for success rates
4. **Content Quality**: Review generated content for improvements

### Monthly Tasks
1. **Update Dependencies**: `pip install -r requirements.txt --upgrade`
2. **Browser Update**: `playwright install chromium`
3. **Backup Configuration**: Save `accounts/` folder securely
4. **Strategy Review**: Analyze engagement metrics and adjust prompts

## 🚨 Troubleshooting

### LLM Providers Failing
```bash
# Check provider status
python deployment/enhanced_run_daily.py --test-llm

# Common fixes:
1. Re-run cookie setup: python setup_cookies.py
2. Check if logged out of web services
3. Verify internet connection
4. Check rate limits in logs
```

### Social Media Authentication Issues
```bash
# Test platform connections
python executors/master_executor.py --test

# Common fixes:
1. Update passwords in config/accounts.env
2. Check 2FA settings
3. Verify API key permissions
4. Review platform rate limits
```

### Low Content Quality
```bash
# Improve content generation prompts
1. Edit prompts in core/content_scheduler.py
2. Add more context about your niche
3. Specify trending topics
4. Request more engaging formats
```

### Rate Limiting Issues
```bash
# Reduce activity levels
1. Lower daily limits in config
2. Increase delays between actions
3. Add more provider accounts
4. Stagger execution times
```

## 📈 Scaling Options

### Adding More Providers
1. Create additional free accounts for each LLM service
2. Save new cookies with unique filenames
3. Update configuration to include new accounts
4. Increases daily capacity from 125 to 300+ queries

### Geographic Distribution
1. Use VPN or proxy rotation
2. Create accounts from different regions
3. Distribute execution across time zones
4. Reduces detection risk

### Platform Expansion
1. Add new social media platforms
2. Create new executor classes
3. Update content generation prompts
4. Expand queue management

## 🎯 Success Metrics

### Daily Targets
- ✅ Content Generation: 100% success rate
- ✅ Social Media Execution: >80% success rate  
- ✅ Account Health: 0 restrictions
- ✅ Engagement Growth: Increasing followers/interactions
- ✅ System Uptime: >95%

### Weekly Goals
- 🚀 15-20 quality posts across all platforms
- 🚀 Growing engagement rates
- 🚀 No platform restrictions or shadowbans
- 🚀 Consistent content quality
- 🚀 Zero manual intervention required

### Monthly Objectives
- 📈 Measurable follower/subscriber growth
- 📈 Higher engagement rates per post
- 📈 Brand recognition in target communities
- 📈 Sustainable automation without detection
- 📈 Content going viral organically

## 🔐 Security Best Practices

1. **Never commit credentials** to version control
2. **Use strong passwords** for all social media accounts
3. **Enable 2FA** where possible
4. **Rotate API keys** periodically
5. **Monitor for unusual activity** in account dashboards
6. **Keep cookies encrypted** at rest
7. **Use dedicated accounts** for automation only

## 🆘 Support Resources

### Self-Help
1. Check logs in `enhanced_daily_execution.log`
2. Review `EXECUTION_LOG.md` for patterns
3. Test individual components
4. Verify configuration settings

### Common Solutions
- **Cookie expired**: Re-run `python setup_cookies.py`
- **Rate limited**: Reduce activity or add more accounts
- **Content quality**: Improve prompts in scheduler
- **Platform errors**: Check account status and limits

This enhanced system provides enterprise-level social media automation completely free while maintaining professional quality and reliability!
