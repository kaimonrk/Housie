#!/data/data/com.termux/files/usr/bin/bash

echo "🔧 Starting Auto Caller Bot Setup for Termux"

# Update packages
echo "📦 Updating packages..."
pkg update -y && pkg upgrade -y

# Install Python and required packages
echo "🐍 Installing Python and dependencies..."
pkg install python -y
pkg install git -y
pkg install libxml2 libxslt -y

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install pyrogram TgCrypto

echo "✅ Basic setup completed!"