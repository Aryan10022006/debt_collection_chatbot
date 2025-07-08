#!/bin/bash

# Quick start script for DebtBot AI

set -e

echo "🚀 Starting DebtBot AI..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure"
    exit 1
fi

# Start the FastAPI application
echo "🌟 Starting FastAPI server..."
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo "🔄 Press Ctrl+C to stop"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
