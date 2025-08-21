# WhatsApp Chatbot Makefile
# Usage: make <command>

.PHONY: help install install-dev test setup check-env start-dev start-prod start-ngrok stop-ngrok docker-build docker-run docker-stop clean logs health webhook-test

# Default target
help:
	@echo "🤖 WhatsApp Chatbot - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  setup        - Run complete setup (install + test)"
	@echo "  check-env    - Check environment variables"
	@echo ""
	@echo "🚀 Development:"
	@echo "  start-dev    - Start development server with auto-reload"
	@echo "  start-ngrok  - Start ngrok tunnel (requires app running)"
	@echo "  stop-ngrok   - Stop ngrok tunnel"
	@echo ""
	@echo "🏭 Production:"
	@echo "  start-prod   - Start production server"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose (includes Redis)"
	@echo "  docker-stop  - Stop Docker containers"
	@echo ""
	@echo "🧪 Testing & Monitoring:"
	@echo "  test         - Run all tests"
	@echo "  health       - Check application health"
	@echo "  webhook-test - Test webhook endpoint"
	@echo "  logs         - Show application logs"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean        - Clean up temporary files"
	@echo "  clean-sessions - Clear all chat sessions"

# Variables
PYTHON := python3
PIP := pip3
APP_NAME := whatsapp-chatbot
DOCKER_IMAGE := $(APP_NAME)
DOCKER_TAG := latest

# Setup & Installation
install:
	@echo "📦 Installing production dependencies..."
	$(PIP) install -r requirements.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	$(PIP) install -r requirements.txt
	@echo "✅ Development dependencies installed"

setup: install-dev check-env test
	@echo "🎉 Setup complete! You can now run 'make start-dev'"

check-env:
	@echo "🔍 Checking environment variables..."
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Please create one from env.example"; \
		exit 1; \
	fi
	@$(PYTHON) -c "from config import settings; print('✅ Environment variables loaded successfully')"

# Development Commands
start-dev:
	@echo "🚀 Starting development server..."
	@echo "📱 Application will be available at: http://localhost:8000"
	@echo "📚 API docs at: http://localhost:8000/docs"
	@echo "🔄 Auto-reload enabled"
	@echo "⏹️  Press Ctrl+C to stop"
	@echo ""
	$(PYTHON) main.py

start-ngrok:
	@echo "🌐 Starting ngrok tunnel..."
	@echo "📱 Make sure your app is running first (make start-dev)"
	@echo "🔗 Copy the HTTPS URL and configure in Twilio console"
	@echo ""
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "❌ FastAPI app is not running on port 8000"; \
		echo "Please start the app first with: make start-dev"; \
		exit 1; \
	fi
	@echo "✅ FastAPI app is running, starting ngrok..."
	ngrok http 8000 --region us --log=stdout

stop-ngrok:
	@echo "🛑 Stopping ngrok tunnel..."
	@pkill -f ngrok || echo "No ngrok process found"

# Production Commands
start-prod:
	@echo "🏭 Starting production server..."
	@echo "📱 Application will be available at: http://localhost:8000"
	@echo "⏹️  Press Ctrl+C to stop"
	@echo ""
	uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1

# Docker Commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run:
	@echo "🐳 Starting with Docker Compose (includes Redis)..."
	@echo "📱 Application will be available at: http://localhost:8000"
	@echo "🔴 Redis will be available at: localhost:6379"
	@echo "⏹️  Press Ctrl+C to stop"
	@echo ""
	docker-compose up --build

docker-stop:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

# Testing & Monitoring
test:
	@echo "🧪 Running tests..."
	@if [ -f test_setup.py ]; then \
		$(PYTHON) test_setup.py; \
	else \
		echo "⚠️  No test_setup.py found, skipping tests"; \
	fi

health:
	@echo "🏥 Checking application health..."
	@curl -s http://localhost:8000/health | $(PYTHON) -m json.tool || echo "❌ Application not running"

webhook-test:
	@echo "🔗 Testing webhook endpoint..."
	@curl -X POST http://localhost:8000/webhook \
		-H "Content-Type: application/x-www-form-urlencoded" \
		-d "From=whatsapp:+1234567890&To=whatsapp:+14155238886&Body=Hello&MessageSid=test123" \
		-s | head -c 200

logs:
	@echo "📋 Application logs (last 50 lines):"
	@if [ -d logs ]; then \
		tail -n 50 logs/*.log 2>/dev/null || echo "No log files found"; \
	else \
		echo "No logs directory found"; \
	fi

# Maintenance
clean:
	@echo "🧹 Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.log" -delete
	@echo "✅ Cleanup complete"

clean-sessions:
	@echo "🗑️  Clearing all chat sessions..."
	@curl -X DELETE http://localhost:8000/sessions/all 2>/dev/null || echo "❌ Could not clear sessions (app may not be running)"

# Utility Commands
status:
	@echo "📊 Application Status:"
	@echo "  - App running: $$(curl -s http://localhost:8000/health > /dev/null && echo "✅" || echo "❌")"
	@echo "  - ngrok running: $$(pgrep ngrok > /dev/null && echo "✅" || echo "❌")"
	@echo "  - Redis running: $$(redis-cli ping > /dev/null 2>&1 && echo "✅" || echo "❌")"
	@echo "  - Docker containers: $$(docker-compose ps --services 2>/dev/null | wc -l | tr -d ' ') running"

restart-dev: stop-ngrok
	@echo "🔄 Restarting development environment..."
	@make start-dev

# Development workflow
dev: start-dev
	@echo "💡 In another terminal, run: make start-ngrok"

# Quick start for new users
quick-start: setup start-dev
	@echo "🎉 Quick start complete!"
	@echo "💡 In another terminal, run: make start-ngrok"
	@echo "📱 Then configure Twilio webhook with the ngrok URL"
