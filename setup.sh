#!/bin/bash
# SocialFlow AI - Installation and Setup Script

echo "🚀 Setting up SocialFlow AI..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p accounts
mkdir -p archive
mkdir -p logs
mkdir -p screenshots

# Copy configuration template
echo "⚙️ Setting up configuration..."
if [ ! -f "config/accounts.env" ]; then
    cp config/accounts_template.env config/accounts.env
    echo "📝 Please edit config/accounts.env with your actual API keys and credentials"
fi

# Set executable permissions
chmod +x deployment/run_daily.py
chmod +x setup.sh

# Create cron job (optional)
echo "⏰ Setting up daily cron job..."
read -p "Do you want to set up daily execution at 10 AM? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add cron job
    (crontab -l 2>/dev/null; echo "0 10 * * * cd $(pwd) && ./venv/bin/python deployment/run_daily.py") | crontab -
    echo "✅ Cron job added - will run daily at 10 AM"
fi

echo "🎉 SocialFlow AI setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit config/accounts.env with your API keys"
echo "2. Generate content using Perplexity and save to content_queue/"
echo "3. Run: python deployment/run_daily.py"
echo ""
echo "For testing authentication: python executors/master_executor.py --test"
