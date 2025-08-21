#!/bin/bash

# WhatsApp Chatbot ngrok Tunnel Setup Script

echo "🌐 Setting up ngrok tunnel for WhatsApp Chatbot..."

# Check if FastAPI app is running
echo "🔍 Checking if FastAPI app is running on port 8000..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ FastAPI app is not running on port 8000"
    echo "Please start the app first with: python main.py"
    echo "Or in another terminal: ./start.sh"
    exit 1
fi

echo "✅ FastAPI app is running on port 8000"

# Start ngrok tunnel
echo "🚀 Starting ngrok tunnel..."
echo "📱 Your webhook URL will be displayed below"
echo "🔗 Copy the HTTPS URL and configure it in Twilio console"
echo ""

# Start ngrok with specific port and region
ngrok http 8000 --region us --log=stdout

echo ""
echo "💡 Tips:"
echo "1. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)"
echo "2. Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox Settings"
echo "3. Set webhook URL to: https://abc123.ngrok.io/webhook"
echo "4. Method: POST"
echo "5. Save the configuration"
echo ""
echo "🔄 Keep this terminal open to maintain the tunnel"
echo "⏹️  Press Ctrl+C to stop the tunnel"
