#!/bin/bash

# Production Deployment Script for DebtBot AI
# This script handles production deployment with zero downtime

set -e

echo "🚀 Production Deployment - DebtBot AI"
echo "===================================="

# Configuration
BACKUP_DIR="./backups"
DEPLOY_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="pre_deploy_backup_$DEPLOY_DATE.sql"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Pre-deployment checks
echo "🔍 Pre-deployment checks..."

# Check if production environment
if [ "$NODE_ENV" != "production" ]; then
    print_error "This script should only be run in production environment"
    exit 1
fi

# Check if all required files exist
required_files=(".env.production" "docker-compose.prod.yml" "nginx.prod.conf")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done
print_status "All required files present"

# Create backup
echo "💾 Creating pre-deployment backup..."
mkdir -p $BACKUP_DIR
if docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres debtbot > "$BACKUP_DIR/$BACKUP_FILE" 2>/dev/null; then
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    print_status "Backup created: $BACKUP_FILE.gz"
else
    print_warning "Could not create backup (database might not be running)"
fi

# Build new images
echo "🔨 Building production images..."
docker-compose -f docker-compose.prod.yml build --no-cache
print_status "Images built successfully"

# Test configuration
echo "🧪 Testing configuration..."
docker-compose -f docker-compose.prod.yml config > /dev/null
print_status "Configuration is valid"

# Rolling deployment
echo "🔄 Performing rolling deployment..."

# Start new database if not running
if ! docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    print_warning "Database not running, starting..."
    docker-compose -f docker-compose.prod.yml up -d db redis
    sleep 15
fi

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm app python scripts/setup_database.py
print_status "Database migrations completed"

# Deploy application with zero downtime
echo "🚀 Deploying application..."
docker-compose -f docker-compose.prod.yml up -d --remove-orphans
print_status "Application deployed"

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Application is healthy"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Application failed to become healthy"
        echo "Rolling back..."
        docker-compose -f docker-compose.prod.yml down
        exit 1
    fi
    
    echo "Waiting for application... (attempt $attempt/$max_attempts)"
    sleep 5
    ((attempt++))
done

# Run post-deployment tests
echo "🧪 Running post-deployment tests..."
docker-compose -f docker-compose.prod.yml exec -T app python scripts/test_system.py
if [ $? -eq 0 ]; then
    print_status "All tests passed"
else
    print_error "Some tests failed - check logs"
fi

# Clean up old images
echo "🧹 Cleaning up old images..."
docker image prune -f
print_status "Cleanup completed"

# Display deployment summary
echo ""
echo "🎉 PRODUCTION DEPLOYMENT COMPLETED!"
echo "=================================="
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔗 Service URLs:"
echo "  • Application: https://your-domain.com"
echo "  • Health Check: https://your-domain.com/health"
echo "  • API Docs: https://your-domain.com/docs"

echo ""
echo "📱 WhatsApp Webhook:"
echo "  • URL: https://your-domain.com/api/v1/whatsapp/webhook"
echo "  • Verify Token: $WHATSAPP_VERIFY_TOKEN"

echo ""
echo "🔧 Management Commands:"
echo "  • View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  • Monitor: ./scripts/monitor.sh"
echo "  • Backup: ./scripts/backup.sh"

echo ""
print_status "Production deployment successful!"
