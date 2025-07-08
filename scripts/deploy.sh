#!/bin/bash

# DebtBot AI Deployment Script

set -e

echo "🚀 Deploying DebtBot AI..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t debtbot-ai:latest .

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start services
echo "▶️ Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Run database setup
echo "🗄️ Setting up database..."
docker-compose exec app python scripts/setup_database.py

# Test WhatsApp integration
echo "📱 Testing WhatsApp integration..."
docker-compose exec app python scripts/test_whatsapp.py

# Check health
echo "🏥 Checking application health..."
curl -f http://localhost:8000/health || exit 1

echo "🎉 Deployment completed successfully!"
echo "Application is running at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "WhatsApp Webhook URL: https://your-domain.com/api/v1/whatsapp/webhook"
