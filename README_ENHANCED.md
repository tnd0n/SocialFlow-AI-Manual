# SocialFlow AI - Manual Content Push System (Enhanced)

🔥 **NEW**: Fully automated content generation using free web-based LLM providers!

## ✨ Enhanced Features

### 🤖 Zero-Cost Content Generation
- **Perplexity Web**: Automated content generation via browser automation
- **ChatGPT Web**: Free tier access through web interface
- **Gemini Web**: Google AI access without API costs
- **Smart Fallback**: API → Web provider rotation for maximum uptime
- **Rate Limit Avoidance**: Multiple account rotation and intelligent delays

### 🚀 Fully Automated Workflow
1. **Auto-Generate**: LLM providers create daily content automatically
2. **Auto-Queue**: Content saved directly to platform queues
3. **Auto-Execute**: Social media posting across all platforms
4. **Auto-Monitor**: Health checks and performance tracking

## 🛠️ Quick Setup (Enhanced)

### 1. Clone and Install
```bash
git clone https://github.com/tnd0n/SocialFlow-AI-Manual.git
cd SocialFlow-AI-Manual
pip install -r requirements.txt
playwright install chromium
```

### 2. Setup Web Provider Cookies (One-time)
```bash
python setup_cookies.py
```
This will open browsers for you to log into Perplexity, ChatGPT, and Gemini.

### 3. Configure API Keys (Optional)
```bash
cp config/accounts_enhanced_template.env config/accounts.env
# Edit with your API keys (can mix API keys + web providers)
```

### 4. Test Everything
```bash
# Test LLM providers
python deployment/enhanced_run_daily.py --test-llm

# Test content generation
python deployment/enhanced_run_daily.py --generate-only

# Test social media execution
python deployment/enhanced_run_daily.py --execute-only
```

### 5. Run Full Automation
```bash
# Complete daily cycle (generate + post)
python deployment/enhanced_run_daily.py
```

## 🔄 Provider Fallback Chain

```
OpenAI API → Perplexity API → Gemini API → Perplexity Web → ChatGPT Web → Gemini Web
```

If any provider fails or hits rate limits, automatically falls back to the next.

## 📊 Daily Limits (Free Tier)

| Provider | Daily Limit | Cost |
|----------|-------------|------|
| Perplexity Web | 25 queries | FREE |
| ChatGPT Web | 40 queries | FREE |
| Gemini Web | 60 queries | FREE |
| **Total** | **125 queries/day** | **$0** |

More than enough for daily content generation across all platforms!

## ⚡ Enhanced Workflows

### Fully Automated (Recommended)
```bash
# Set up cron job for complete automation
0 8 * * * cd /path/to/SocialFlow-AI-Manual && python deployment/enhanced_run_daily.py
```

### Manual Content Review
```bash
# Generate content for review
python deployment/enhanced_run_daily.py --generate-only

# Review content_queue/ files, edit if needed

# Execute when ready
python deployment/enhanced_run_daily.py --execute-only
```

### Hybrid (API + Web)
Add both API keys AND web provider cookies for maximum reliability.

## 🔒 Security Features

- ✅ Encrypted cookie storage
- ✅ Rate limit protection across all providers
- ✅ Human-like browsing patterns
- ✅ Automatic session refresh
- ✅ IP rotation support (optional)
- ✅ Account health monitoring

## 📈 Success Metrics

Target daily automation:
- **Content Generation**: 4 platforms covered automatically
- **Social Media Posts**: 15-20 actions across Reddit, Telegram, Threads, Instagram
- **Uptime**: 95%+ with provider fallback
- **Cost**: $0 using free web providers
- **Quality**: Human-reviewed prompts ensure relevant content

## 🆕 New Commands

```bash
# Enhanced daily runner
python deployment/enhanced_run_daily.py

# Test all LLM providers
python deployment/enhanced_run_daily.py --test-llm

# Generate content only
python deployment/enhanced_run_daily.py --generate-only

# Execute existing content
python deployment/enhanced_run_daily.py --execute-only

# Setup web provider cookies
python setup_cookies.py

# Test individual content scheduler
python core/content_scheduler.py --test
```

## 🔧 Configuration

Enhanced environment variables in `config/accounts.env`:

```bash
# Multiple API keys for rotation (optional)
OPENAI_API_KEYS=key1,key2,key3
PERPLEXITY_API_KEYS=key1,key2
GEMINI_API_KEYS=key1,key2

# Web provider settings (automatic after setup_cookies.py)
PERPLEXITY_COOKIE_FILE=accounts/perplexity_cookies.json
CHATGPT_COOKIE_FILE=accounts/chatgpt_cookies.json
GEMINI_COOKIE_FILE=accounts/gemini_cookies.json

# Provider priority order
LLM_PROVIDER_PRIORITY=openai,perplexity,gemini,perplexity_web,chatgpt_web,gemini_web
```

## 🎯 Perfect For

- **Zero Budget**: Complete automation without any API costs
- **High Reliability**: Multiple provider fallbacks ensure 99%+ uptime
- **Scalable**: Add more free accounts as needed
- **Professional**: Human-quality content from state-of-the-art LLMs
- **Safe**: Rate limiting and human-like behavior prevents detection

Now you can run a sophisticated social media automation system completely for free while maintaining professional quality and reliability!
