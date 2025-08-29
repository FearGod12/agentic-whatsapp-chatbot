# 🤖 Agentic WhatsApp Chatbot

A powerful WhatsApp chatbot built with FastAPI, Twilio, and OpenAI that provides intelligent conversational responses.

## 🚀 Features

- **WhatsApp Integration**: Seamless integration with WhatsApp via Twilio
- **AI-Powered Responses**: Intelligent responses using OpenAI's GPT models
- **Session Management**: Maintains conversation context for each user
- **RESTful API**: Clean FastAPI endpoints for monitoring and management
- **Security**: Webhook signature validation and environment-based configuration
- **Scalable**: Built with modern async Python for high performance

## 🏗️ Architecture

```
User → WhatsApp → Twilio → FastAPI Webhook → OpenAI → Response → Twilio → WhatsApp → User
```

## 📋 Prerequisites

- Python 3.8+
- Twilio Account (with WhatsApp Sandbox or Business API)
- OpenAI API Key
- Public HTTPS endpoint (for Twilio webhooks)

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd agentic-whatsapp-chatbot
   ```

2. **Set up environment variables**

   ```bash
   cp env.example .env
   ```

   Edit `.env` with your credentials:

   ```env
   # Twilio Configuration
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
   TWILIO_PHONE_NUMBER=whatsapp:+14155238886

   # OpenAI Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o

   # Redis Configuration (Optional - falls back to in-memory if not available)
   REDIS_URL=redis://localhost:6379
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   REDIS_PASSWORD=
   REDIS_USE_SSL=False
   SESSION_TTL=86400

   # FastAPI Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=True

   # Security
   SECRET_KEY=your_secret_key_here
   ```

3. **Quick setup with Makefile**
   ```bash
   make quick-start
   ```

## 🚀 Running the Application

### Quick Start (Recommended)

```bash
# Complete setup and start development server
make quick-start

# In another terminal, start ngrok tunnel
make start-ngrok
```

### Manual Commands

#### Development Mode

```bash
make start-dev
```

#### Production Mode

```bash
make start-prod
```

#### Docker (includes Redis)

```bash
make docker-run
```

The application will be available at `http://localhost:8000`

## 🌐 Local Development with ngrok

For testing Twilio webhooks locally:

### Quick Setup

```bash
# Terminal 1: Start chatbot
make start-dev

# Terminal 2: Start ngrok tunnel
make start-ngrok
```

### Manual Commands

```bash
# Start ngrok tunnel
make start-ngrok

# Stop ngrok tunnel
make stop-ngrok
```

See [NGROK_SETUP.md](NGROK_SETUP.md) for detailed instructions.

## 🔧 Makefile Commands

The project includes a comprehensive Makefile for easy management:

### Quick Commands

```bash
make help          # Show all available commands
make quick-start   # Complete setup and start development
make status        # Check application status
```

### Development

```bash
make setup         # Install dependencies and run tests
make start-dev     # Start development server
make start-ngrok   # Start ngrok tunnel
make stop-ngrok    # Stop ngrok tunnel
make restart-dev   # Restart development environment
```

### Production

```bash
make start-prod    # Start production server
make docker-run    # Run with Docker Compose (includes Redis)
make docker-stop   # Stop Docker containers
```

### Testing & Monitoring

```bash
make test          # Run all tests
make health        # Check application health
make webhook-test  # Test webhook endpoint
make logs          # Show application logs
```

### Maintenance

```bash
make clean         # Clean temporary files
make clean-sessions # Clear all chat sessions
```

## 📱 Twilio Setup

1. **Create a Twilio Account**

   - Sign up at [twilio.com](https://www.twilio.com)
   - Get your Account SID and Auth Token

2. **Set up WhatsApp Sandbox**

   - Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
   - Follow the instructions to join your sandbox

3. **Configure Webhook**
   - In Twilio Console → Messaging → Settings → WhatsApp Sandbox Settings
   - Set the webhook URL to: `https://your-domain.com/webhook`
   - Method: POST

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Application status and information
- `GET /health` - Health check endpoint
- `POST /webhook` - Twilio webhook endpoint (receives WhatsApp messages)

### Management Endpoints

- `GET /sessions` - Get count of active chat sessions
- `GET /sessions/{user_phone}` - Get specific user session info
- `DELETE /sessions/{user_phone}` - Clear user session
- `POST /send-message` - Send test message to user
- `GET /storage/status` - Get Redis connection and storage status

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📁 Project Structure

```
agentic-whatsapp-chatbot/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── README.md             # This file
└── services/
    ├── chat_service.py    # Chat session management
    ├── openai_service.py  # OpenAI API integration
    └── twilio_service.py  # Twilio API integration
```

## 🔒 Security Features

- **Environment Variables**: All secrets stored in `.env` file
- **Webhook Validation**: Optional Twilio signature validation
- **Input Validation**: Pydantic models for request/response validation
- **Error Handling**: Comprehensive error handling and logging

## 💾 Session Storage & Context Management

### Current Implementation (Production Ready)

- **Primary Storage**: Redis with automatic TTL (24 hours)
- **Fallback Storage**: In-memory storage if Redis unavailable
- **User Identification**: Phone number from Twilio webhook
- **Context**: Maintains conversation history per user
- **Cleanup**: Automatic session expiration and cleanup

### Storage Features

- **Redis Primary**: Fast, persistent session storage with TTL
- **Graceful Fallback**: Automatically falls back to in-memory if Redis unavailable
- **Session Persistence**: Sessions survive server restarts when Redis is used
- **Multi-user Support**: Each phone number gets independent conversation
- **Context Preservation**: AI remembers previous messages in conversation
- **Session Isolation**: Users cannot see each other's conversations
- **Automatic Cleanup**: Expired sessions are removed automatically

### Redis Configuration

Add these to your `.env` file for Redis support:

```env
# Redis Configuration (Optional - falls back to in-memory if not available)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_USE_SSL=False
SESSION_TTL=86400
```

### Storage Monitoring

- **Health Check**: `/health` - Basic application health
- **Storage Status**: `/storage/status` - Redis connection and storage info
- **Session Count**: `/sessions` - Number of active sessions
- **Session Details**: `/sessions/{user_phone}` - Specific session information

### Docker Setup with Redis

The included `docker-compose.yml` provides Redis out of the box:

```bash
docker-compose up
```

This starts both the chatbot and Redis services together.

## 🧪 Testing

### Manual Testing

1. **Start the application**

   ```bash
   python main.py
   ```

2. **Test health endpoint**

   ```bash
   curl http://localhost:8000/health
   ```

3. **Test webhook (simulate Twilio)**
   ```bash
   curl -X POST http://localhost:8000/webhook \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "From=whatsapp:+1234567890&To=whatsapp:+14155238886&Body=Hello&MessageSid=test123"
   ```

### WhatsApp Testing

1. Join your Twilio WhatsApp sandbox
2. Send a message to the sandbox number
3. Verify the bot responds

## 📊 Monitoring

### Logs

The application logs all activities including:

- Incoming webhooks
- OpenAI API calls
- Error messages
- Session management

### Metrics

- Active session count via `/sessions` endpoint
- Health status via `/health` endpoint

## 🚀 Deployment

### Using Docker

1. **Create Dockerfile**

   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run**
   ```bash
   docker build -t whatsapp-chatbot .
   docker run -p 8000:8000 --env-file .env whatsapp-chatbot
   ```

### Using Cloud Platforms

- **Heroku**: Deploy with `Procfile` and environment variables
- **Railway**: Connect GitHub repo and set environment variables
- **DigitalOcean App Platform**: Deploy with Docker
- **AWS/GCP**: Deploy to container services

## 🔧 Configuration Options

### OpenAI Settings

- `OPENAI_MODEL`: GPT model to use (default: gpt-3.5-turbo)
- `OPENAI_API_KEY`: Your OpenAI API key

### Twilio Settings

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_PHONE_NUMBER`: Your Twilio WhatsApp number

### Application Settings

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: True)

## 🐛 Troubleshooting

### Common Issues

1. **Webhook not receiving messages**

   - Verify webhook URL is publicly accessible
   - Check Twilio console webhook configuration
   - Ensure HTTPS is enabled

2. **OpenAI API errors**

   - Verify API key is correct
   - Check API quota and billing
   - Ensure model name is valid

3. **Session management issues**
   - Check application logs for errors
   - Verify session cleanup is working
   - Monitor memory usage

### Debug Mode

Enable debug mode in `.env`:

```env
DEBUG=True
```

This will provide detailed logging and auto-reload on code changes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

