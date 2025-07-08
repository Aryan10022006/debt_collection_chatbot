#!/bin/bash

echo "🚀 Starting AI Debt Collection Chatbot..."
echo "========================================"

# Check Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis python-multipart
pip install googletrans==4.0.0rc1 langdetect httpx python-jose[cryptography]
pip install jinja2 python-dotenv asyncpg alembic

# Create templates directory
mkdir -p templates

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://debt_user:debt_password@localhost/debt_collection_db"
export XAI_API_KEY="${XAI_API_KEY:-demo_key}"
export GROQ_API_KEY="${GROQ_API_KEY:-demo_key}"
export WHATSAPP_VERIFY_TOKEN="debt_collection_webhook_verify_2024"

# Start the application
echo "🎉 Starting the chatbot server..."
echo "🌐 Web Interface: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "💬 WhatsApp Webhook: http://localhost:8000/api/v1/whatsapp/webhook"
echo ""

python main.py
