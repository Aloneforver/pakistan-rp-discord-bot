#!/usr/bin/env bash
# Build script for Render deployment

echo "🔧 Starting build process..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs backups transcripts rule_database automation announcements database

# Set permissions
echo "🔐 Setting permissions..."
chmod +x main.py

echo "✅ Build completed successfully!"
echo "🚀 Ready for deployment!"