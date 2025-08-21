# 🌐 ngrok Setup Guide for WhatsApp Chatbot

This guide will help you expose your local WhatsApp chatbot to the internet using ngrok for Twilio webhook testing.

## 📋 Prerequisites

- ✅ ngrok installed (already done)
- ✅ WhatsApp chatbot running locally
- ✅ Twilio account with WhatsApp Sandbox

## 🚀 Quick Start

### Step 1: Start Your Chatbot

First, start your WhatsApp chatbot locally:

```bash
# Option 1: Direct start
python main.py

# Option 2: Using the startup script
./start.sh
```

Your chatbot should be running at `http://localhost:8000`

### Step 2: Start ngrok Tunnel

In a **new terminal window**, run:

```bash
./start_ngrok.sh
```

This will:

- ✅ Check if your app is running
- 🚀 Start ngrok tunnel
- 📱 Display your public HTTPS URL

### Step 3: Configure Twilio Webhook

1. **Copy the HTTPS URL** from ngrok output (e.g., `https://abc123.ngrok.io`)
2. **Go to Twilio Console**: https://console.twilio.com/
3. **Navigate to**: Messaging → Settings → WhatsApp Sandbox Settings
4. **Set Webhook URL**: `https://abc123.ngrok.io/webhook`
5. **Method**: POST
6. **Save** the configuration

## 🔧 Manual ngrok Commands

If you prefer to run ngrok manually:

```bash
# Basic tunnel
ngrok http 8000

# With specific region (recommended)
ngrok http 8000 --region us

# With custom subdomain (requires ngrok account)
ngrok http 8000 --subdomain=mywhatsappbot

# With authentication (requires ngrok account)
ngrok http 8000 --authtoken=your_auth_token
```

## 📱 Testing Your Setup

### 1. Test Local Health

```bash
curl http://localhost:8000/health
```

### 2. Test ngrok Tunnel

```bash
curl https://your-ngrok-url.ngrok.io/health
```

### 3. Test Webhook (Simulate Twilio)

```bash
curl -X POST https://your-ngrok-url.ngrok.io/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&To=whatsapp:+14155238886&Body=Hello&MessageSid=test123"
```

### 4. Test with WhatsApp

1. Join your Twilio WhatsApp sandbox
2. Send a message to the sandbox number
3. Check your chatbot logs for incoming webhooks

## 🔍 Troubleshooting

### ngrok Not Starting

```bash
# Check if port 8000 is available
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Webhook Not Receiving Messages

- ✅ Verify ngrok tunnel is active
- ✅ Check Twilio webhook URL is correct
- ✅ Ensure `/webhook` endpoint is included
- ✅ Verify HTTPS (not HTTP) URL

### ngrok URL Changes

- Free ngrok accounts get new URLs each time
- Update Twilio webhook URL when ngrok restarts
- Consider ngrok account for static URLs

## 🔒 Security Considerations

### For Development Only

- ngrok exposes your local server to the internet
- Use only for development and testing
- Don't use for production deployments

### ngrok Account Benefits

- **Static URLs**: Same URL every time
- **Custom Domains**: Use your own subdomain
- **Password Protection**: Add basic auth
- **Request Inspection**: View all webhook requests

## 📊 Monitoring

### Check ngrok Status

Visit: `http://localhost:4040` (ngrok web interface)

### Monitor Webhooks

- Check your chatbot logs
- Use ngrok web interface to inspect requests
- Monitor Twilio console for webhook delivery status

## 🎯 Production Deployment

For production, use proper hosting instead of ngrok:

- **Heroku**: `heroku create && git push heroku main`
- **Railway**: Connect GitHub repo
- **DigitalOcean**: Deploy with Docker
- **AWS/GCP**: Container services

## 📝 Example ngrok Output

```
Session Status                online
Account                       your-email@example.com
Version                       3.26.0
Region                        United States (us)
Latency                       51ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

## 🆘 Common Issues

### "Tunnel not found"

- Restart ngrok
- Check if port 8000 is free

### "Webhook timeout"

- Check your chatbot is running
- Verify ngrok tunnel is active

### "Invalid webhook URL"

- Ensure HTTPS URL
- Include `/webhook` path
- Check for typos

---

**Happy testing! 🚀📱**
