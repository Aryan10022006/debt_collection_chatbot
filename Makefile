# DebtBot AI - FastAPI Makefile

.PHONY: help install setup run test clean docker-build docker-run

help:
	@echo "🤖 DebtBot AI - FastAPI Commands"
	@echo "================================"
	@echo "install     - Install Python dependencies"
	@echo "setup       - Complete system setup"
	@echo "run         - Start FastAPI development server"
	@echo "test        - Run system tests"
	@echo "check       - Check dependencies"
	@echo "clean       - Clean up temporary files"
	@echo "docker-build - Build Docker image"
	@echo "docker-run  - Run with Docker Compose"

install:
	@echo "📦 Installing Python dependencies..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

setup:
	@echo "🚀 Running complete setup..."
	chmod +x setup.sh
	./setup.sh

run:
	@echo "🌟 Starting FastAPI server..."
	. venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	@echo "🧪 Running system tests..."
	. venv/bin/activate && python scripts/test_system.py

check:
	@echo "🔍 Checking dependencies..."
	. venv/bin/activate && python scripts/check_dependencies.py

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t debtbot-ai:latest .

docker-run:
	@echo "🚀 Starting with Docker Compose..."
	docker-compose up -d
	@echo "⏳ Waiting for services..."
	sleep 10
	docker-compose exec app python scripts/setup_database.py

dev:
	@echo "🔧 Starting development environment..."
	. venv/bin/activate && python scripts/setup_database.py
	. venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

prod:
	@echo "🚀 Starting production server..."
	. venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

logs:
	@echo "📋 Showing application logs..."
	docker-compose logs -f app

stop:
	@echo "🛑 Stopping services..."
	docker-compose down

restart:
	@echo "🔄 Restarting services..."
	docker-compose restart
