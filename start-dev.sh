#!/bin/bash
echo "🔧 Starting AI Debt Collection Chatbot in Development Mode"
echo "🐍 Pure Python FastAPI with auto-reload"
echo "❌ NO Node.js | NO Express.js | NO JavaScript Frameworks"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install development dependencies if needed
echo "📦 Checking development dependencies..."
python3 -c "import watchdog" 2>/dev/null || pip3 install watchdog

echo "🚀 Starting FastAPI server with auto-reload..."
echo "🌐 Access at: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"
echo ""

# Start with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
