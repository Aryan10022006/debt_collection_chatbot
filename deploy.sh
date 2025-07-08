#!/bin/bash

# DebtBot AI - Complete Deployment Script
# FastAPI-based multilingual debt collection chatbot

set -e

echo "🚀 Deploying DebtBot AI - Complete System..."
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check system requirements
print_info "Checking system requirements..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.11+ required. Current version: $python_version"
    exit 1
fi
print_status "Python version: $python_version"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is required but not installed"
    print_info "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
print_status "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is required but not installed"
    print_info "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
print_status "Docker Compose is installed"

# Create project directory structure
print_info "Setting up project structure..."
mkdir -p {logs,data,ssl,backups,scripts}
print_status "Project directories created"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating environment configuration..."
    cp .env.example .env
    print_warning "Please edit .env file with your actual credentials"
    print_info "Required variables:"
    echo "  - WHATSAPP_ACCESS_TOKEN"
    echo "  - WHATSAPP_PHONE_NUMBER_ID"
    echo "  - OPENAI_API_KEY (optional)"
    echo "  - DATABASE_URL"
    echo ""
    read -p "Press Enter after configuring .env file..."
fi

# Validate environment variables
print_info "Validating environment configuration..."
source .env

required_vars=("WHATSAPP_ACCESS_TOKEN" "WHATSAPP_PHONE_NUMBER_ID" "WHATSAPP_VERIFY_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set"
        exit 1
    fi
done
print_status "Environment variables validated"

# Build Docker images
print_info "Building Docker images..."
docker-compose build --no-cache
print_status "Docker images built successfully"

# Start database services first
print_info "Starting database services..."
docker-compose up -d db redis
print_status "Database services started"

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 15

# Check database connectivity
print_info "Testing database connectivity..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        print_status "Database is ready"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Database failed to start after $max_attempts attempts"
        docker-compose logs db
        exit 1
    fi
    
    print_info "Waiting for database... (attempt $attempt/$max_attempts)"
    sleep 2
    ((attempt++))
done

# Initialize database
print_info "Initializing database schema..."
docker-compose run --rm app python scripts/setup_database.py
print_status "Database initialized"

# Start all services
print_info "Starting all services..."
docker-compose up -d
print_status "All services started"

# Wait for application to be ready
print_info "Waiting for application to be ready..."
sleep 10

# Health check
print_info "Performing health check..."
max_attempts=20
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Application is healthy"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "Application health check failed after $max_attempts attempts"
        docker-compose logs app
        exit 1
    fi
    
    print_info "Waiting for application... (attempt $attempt/$max_attempts)"
    sleep 3
    ((attempt++))
done

# Test WhatsApp integration
print_info "Testing WhatsApp integration..."
docker-compose exec -T app python scripts/test_whatsapp.py
print_status "WhatsApp integration tested"

# Run comprehensive system tests
print_info "Running system tests..."
docker-compose exec -T app python scripts/test_system.py
print_status "System tests completed"

# Setup SSL certificates (if in production)
if [ "$NODE_ENV" = "production" ]; then
    print_info "Setting up SSL certificates..."
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_warning "SSL certificates not found"
        print_info "Generating self-signed certificates for testing..."
        mkdir -p ssl
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=DebtBot AI/CN=localhost"
        print_status "Self-signed certificates generated"
        print_warning "For production, replace with valid SSL certificates"
    fi
fi

# Setup log rotation
print_info "Setting up log rotation..."
cat > /tmp/debtbot-logrotate << EOF
/var/log/debtbot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart app > /dev/null 2>&1 || true
    endscript
}
EOF

if [ -w /etc/logrotate.d ]; then
    sudo mv /tmp/debtbot-logrotate /etc/logrotate.d/debtbot
    print_status "Log rotation configured"
else
    print_warning "Could not configure log rotation (requires sudo)"
fi

# Create backup script
print_info "Creating backup script..."
cat > scripts/backup.sh << 'EOF'
#!/bin/bash
# Database backup script for DebtBot AI

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="debtbot_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

echo "Creating database backup..."
docker-compose exec -T db pg_dump -U postgres debtbot > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    echo "✅ Backup compressed: $BACKUP_FILE.gz"
    
    # Keep only last 7 days of backups
    find $BACKUP_DIR -name "debtbot_backup_*.sql.gz" -mtime +7 -delete
    echo "✅ Old backups cleaned up"
else
    echo "❌ Backup failed"
    exit 1
fi
EOF

chmod +x scripts/backup.sh
print_status "Backup script created"

# Create monitoring script
print_info "Creating monitoring script..."
cat > scripts/monitor.sh << 'EOF'
#!/bin/bash
# System monitoring script for DebtBot AI

echo "🔍 DebtBot AI System Status"
echo "=========================="

# Check container status
echo "📦 Container Status:"
docker-compose ps

echo ""
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo ""
echo "🏥 Health Checks:"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application: Healthy"
else
    echo "❌ Application: Unhealthy"
fi

if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database: Ready"
else
    echo "❌ Database: Not ready"
fi

if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: Connected"
else
    echo "❌ Redis: Disconnected"
fi

echo ""
echo "📊 Recent Logs (last 10 lines):"
docker-compose logs --tail=10 app
EOF

chmod +x scripts/monitor.sh
print_status "Monitoring script created"

# Create systemd service (if systemd is available)
if command -v systemctl &> /dev/null; then
    print_info "Creating systemd service..."
    
    cat > /tmp/debtbot.service << EOF
[Unit]
Description=DebtBot AI Chatbot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    if [ -w /etc/systemd/system ]; then
        sudo mv /tmp/debtbot.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable debtbot.service
        print_status "Systemd service created and enabled"
    else
        print_warning "Could not create systemd service (requires sudo)"
    fi
fi

# Final deployment verification
print_info "Performing final deployment verification..."

# Check all endpoints
endpoints=(
    "http://localhost:8000/health"
    "http://localhost:8000/docs"
    "http://localhost:8000/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=${WHATSAPP_VERIFY_TOKEN}&hub.challenge=test"
)

for endpoint in "${endpoints[@]}"; do
    if curl -f "$endpoint" > /dev/null 2>&1; then
        print_status "Endpoint accessible: $endpoint"
    else
        print_warning "Endpoint not accessible: $endpoint"
    fi
done

# Display deployment summary
echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "====================================="
echo ""
print_info "📊 Service URLs:"
echo "  • Application: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Database Admin: http://localhost:8080"
echo ""
print_info "📱 WhatsApp Configuration:"
echo "  • Webhook URL: https://your-domain.com/api/v1/whatsapp/webhook"
echo "  • Verify Token: ${WHATSAPP_VERIFY_TOKEN}"
echo ""
print_info "🔧 Management Commands:"
echo "  • View logs: docker-compose logs -f app"
echo "  • Monitor system: ./scripts/monitor.sh"
echo "  • Create backup: ./scripts/backup.sh"
echo "  • Restart services: docker-compose restart"
echo "  • Stop services: docker-compose down"
echo ""
print_info "📁 Important Files:"
echo "  • Configuration: .env"
echo "  • Logs: logs/"
echo "  • Backups: backups/"
echo "  • SSL Certificates: ssl/"
echo ""
print_warning "🔒 Security Reminders:"
echo "  • Change default passwords in .env"
echo "  • Setup proper SSL certificates for production"
echo "  • Configure firewall rules"
echo "  • Regular security updates"
echo ""
print_info "📞 Next Steps:"
echo "  1. Configure WhatsApp webhook in Meta Developer Console"
echo "  2. Submit message templates for approval"
echo "  3. Test with real phone numbers"
echo "  4. Setup monitoring and alerting"
echo "  5. Configure domain and SSL for production"
echo ""
echo "🚀 DebtBot AI is now running and ready to serve!"
