#!/data/data/com.termux/files/usr/bin/bash

clear
echo "=========================================="
echo "   Auto Caller Bot Installation for Termux"
echo "=========================================="
echo ""

# Update packages
echo "[1/5] 📦 Updating packages..."
pkg update -y
pkg upgrade -y

# Install Python and dependencies
echo "[2/5] 🐍 Installing Python..."
pkg install python -y
pkg install python-pip -y
pkg install git -y
pkg install libxml2 libxslt -y

# Upgrade pip
echo "[3/5] 🔄 Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "[4/5] 📦 Installing Python packages..."
pip install pyrogram TgCrypto

# Create bot directory
echo "[5/5] 📁 Setting up bot..."
mkdir -p ~/auto-caller-bot
cd ~/auto-caller-bot

# Download bot file (you'll need to copy the actual file)
echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy the bot file to Termux:"
echo "   scp auto_caller_bot_termux.py termux:~/auto-caller-bot/"
echo ""
echo "2. Run the bot:"
echo "   cd ~/auto-caller-bot"
echo "   python auto_caller_bot_termux.py"
echo ""
echo "3. First time setup:"
echo "   - You need API_HASH from my.telegram.org"
echo "   - Add it to the script"
echo ""
echo "Need help? Check README.md"
echo "=========================================="