#!/bin/bash

echo "🚀 Deploying Complete AI Debt Collection Chatbot..."
echo "=================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run as root"
    exit 1
fi

# Create project directory
PROJECT_DIR="debt-collection-chatbot"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis python-multipart
pip install googletrans==4.0.0rc1 langdetect httpx python-jose[cryptography]
pip install jinja2 python-dotenv asyncpg alembic

# Setup PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres createdb debt_collection_db
sudo -u postgres psql -c "CREATE USER debt_user WITH PASSWORD 'debt_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE debt_collection_db TO debt_user;"

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://debt_user:debt_password@localhost/debt_collection_db
POSTGRES_USER=debt_user
POSTGRES_PASSWORD=debt_password
POSTGRES_DB=debt_collection_db

# AI Configuration
XAI_API_KEY=${XAI_API_KEY:-your_xai_api_key_here}
GROQ_API_KEY=${GROQ_API_KEY:-your_groq_api_key_here}

# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=debt_collection_webhook_verify_2024
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# Application Configuration
APP_NAME="AI Debt Collection Chatbot"
VERSION="1.0.0"
DEBUG=true
SECRET_KEY=your_secret_key_here
FRONTEND_URL=http://localhost:8000

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
EOF

# Start services
echo "🔄 Starting services..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Run the application
echo "🎉 Starting the chatbot application..."
python main.py

echo "✅ Deployment complete!"
echo "🌐 Access your chatbot at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "💬 WhatsApp webhook: http://localhost:8000/api/v1/whatsapp/webhook"
