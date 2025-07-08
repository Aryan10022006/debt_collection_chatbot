#!/bin/bash

# Quick Start Script - Get DebtBot AI running in 5 minutes

set -e

echo "⚡ DebtBot AI - Quick Start (5 minutes)"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Clone or setup project
if [ ! -f "requirements.txt" ]; then
    echo "❌ Please run this script from the DebtBot AI project directory"
    exit 1
fi

# Quick environment setup
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment..."
    cp .env.example .env
    
    # Generate secure passwords
    DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    REDIS_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    
    # Update .env with generated passwords
    sed -i "s/your_secure_db_password/$DB_PASS/g" .env
    sed -i "s/your_secure_redis_password/$REDIS_PASS/g" .env
    sed -i "s/your_super_secure_secret_key_change_this_in_production/$SECRET_KEY/g" .env
    
    echo "✅ Environment configured with secure passwords"
fi

# Quick build and start
echo "🚀 Starting DebtBot AI..."
docker-compose up -d --build

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 20

# Initialize database
echo "🗄️ Setting up database..."
docker-compose exec -T app python scripts/setup_database.py

# Quick health check
echo "🏥 Checking system health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ System is healthy!"
else
    echo "⚠️ System might still be starting..."
fi

# Display quick access info
echo ""
echo "🎉 DebtBot AI is running!"
echo "======================="
echo ""
echo "📊 Quick Access:"
echo "  • Application: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Health: http://localhost:8000/health"
echo ""
echo "🔧 Quick Commands:"
echo "  • View logs: docker-compose logs -f app"
echo "  • Stop: docker-compose down"
echo "  • Restart: docker-compose restart"
echo ""
echo "📱 WhatsApp Setup:"
echo "  1. Go to Meta Developer Console"
echo "  2. Set webhook URL: https://your-domain.com/api/v1/whatsapp/webhook"
echo "  3. Set verify token: debt_collection_webhook_verify_2024"
echo ""
echo "🚀 Ready to test! Send a message to your WhatsApp Business number."
