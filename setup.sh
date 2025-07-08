#!/bin/bash

# DebtBot AI - Complete Setup Script
# FastAPI-based multilingual debt collection chatbot

set -e

echo "🚀 Setting up DebtBot AI (FastAPI + Python)..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Current version: $python_version"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "📝 Please edit .env file with your credentials before continuing"
    echo "Press Enter when ready..."
    read
fi

# Setup database (PostgreSQL)
echo "🗄️ Setting up database..."
if command -v docker &> /dev/null; then
    echo "🐳 Starting PostgreSQL with Docker..."
    docker run -d \
        --name debtbot-postgres \
        -e POSTGRES_DB=debtbot \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=password \
        -p 5432:5432 \
        postgres:15
    
    echo "⏳ Waiting for PostgreSQL to start..."
    sleep 10
else
    echo "⚠️ Docker not found. Please install PostgreSQL manually"
    echo "Database URL should be: postgresql+asyncpg://postgres:password@localhost:5432/debtbot"
fi

# Setup Redis
echo "🔴 Setting up Redis..."
if command -v docker &> /dev/null; then
    docker run -d \
        --name debtbot-redis \
        -p 6379:6379 \
        redis:7-alpine
else
    echo "⚠️ Docker not found. Please install Redis manually"
fi

# Initialize database
echo "🏗️ Initializing database tables..."
python scripts/setup_database.py

# Test WhatsApp integration
echo "📱 Testing WhatsApp integration..."
python scripts/test_whatsapp.py

echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "📊 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔗 WhatsApp Webhook URL:"
echo "   https://your-domain.com/api/v1/whatsapp/webhook"
