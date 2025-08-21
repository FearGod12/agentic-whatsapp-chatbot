#!/bin/bash

# WhatsApp Chatbot Startup Script

echo "🤖 Starting Agentic WhatsApp Chatbot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy env.example to .env and configure your settings:"
    echo "cp env.example .env"
    echo "Then edit .env with your Twilio and OpenAI credentials."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run setup test
echo "🧪 Running setup test..."
python test_setup.py

# If test passes, start the application
if [ $? -eq 0 ]; then
    echo "🚀 Starting the application..."
    echo "📱 The chatbot will be available at: http://localhost:8000"
    echo "📚 API documentation: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop the application"
    echo ""
    python main.py
else
    echo "❌ Setup test failed. Please fix the issues before starting the application."
    exit 1
fi
