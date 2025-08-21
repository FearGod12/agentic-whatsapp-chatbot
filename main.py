from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
import uvicorn

from config import settings
from models import TwilioWebhookRequest, HealthCheck
from services.chat_service import ChatService
from services.twilio_service import TwilioService
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic WhatsApp Chatbot",
    description="A WhatsApp chatbot powered by FastAPI, Twilio, and OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
chat_service = ChatService()
twilio_service = TwilioService()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic information."""
    return """
    <html>
        <head>
            <title>Agentic WhatsApp Chatbot</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .status { padding: 10px; background: #e8f5e8; border-radius: 5px; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 Agentic WhatsApp Chatbot</h1>
                <div class="status">
                    <strong>Status:</strong> Running ✅
                </div>
                <h2>Endpoints:</h2>
                <div class="endpoint">
                    <strong>POST /webhook</strong> - Twilio webhook endpoint for incoming messages
                </div>
                <div class="endpoint">
                    <strong>GET /health</strong> - Health check endpoint
                </div>
                <div class="endpoint">
                    <strong>GET /sessions</strong> - Get active chat sessions count
                </div>
                <div class="endpoint">
                    <strong>GET /docs</strong> - API documentation
                </div>
                <p><em>Configure your Twilio webhook URL to point to: <code>https://your-domain.com/webhook</code></em></p>
            </div>
        </body>
    </html>
    """


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/webhook/twilio")
async def twilio_webhook(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    NumMedia: Optional[str] = Form(None),
    MediaUrl0: Optional[str] = Form(None),
    MessageTimestamp: Optional[str] = Form(None)
):
    """
    Twilio webhook endpoint for incoming WhatsApp messages.

    This endpoint receives webhooks from Twilio when users send messages to the WhatsApp number.
    It processes the message through OpenAI and sends a response back via Twilio.
    """
    try:
        # Log incoming webhook
        logger.info(f"Received webhook from {From}: {Body[:50]}...")

        # Validate webhook signature (optional but recommended for production)
        # signature = request.headers.get("X-Twilio-Signature")
        # if signature:
        #     if not twilio_service.validate_webhook_signature(signature, str(request.url), dict(request.form())):
        #         logger.warning("Invalid webhook signature")
        #         raise HTTPException(status_code=403, detail="Invalid signature")

        # Extract user phone number (remove whatsapp: prefix)
        user_phone = From.replace("whatsapp:", "")

        # Process the message through chat service
        response_message = await chat_service.process_message(user_phone, Body)

        # Create TwiML response
        twiml_response = twilio_service.create_twiml_response(response_message)

        logger.info(f"Response sent to {user_phone}: {response_message[:50]}...")

        return Response(
            content=twiml_response,
            media_type="application/xml"
        )

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        # Return a simple error response
        error_response = twilio_service.create_twiml_response(
            "I'm sorry, I'm having trouble processing your message right now. Please try again later."
        )
        return Response(
            content=error_response,
            media_type="application/xml"
        )


@app.get("/sessions")
async def get_sessions_info():
    """Get information about active chat sessions."""
    try:
        active_count = chat_service.get_active_sessions_count()
        return {
            "active_sessions": active_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting sessions info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/storage/status")
async def get_storage_status():
    """Get storage status information (Redis connection, fallback storage, etc.)."""
    try:
        storage_status = chat_service.get_storage_status()
        return {
            "storage_status": storage_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting storage status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sessions/{user_phone}")
async def get_session_info(user_phone: str):
    """Get information about a specific user's chat session."""
    try:
        session_info = chat_service.get_session_info(user_phone)
        if session_info:
            return session_info
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info for {user_phone}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sessions/{user_phone}")
async def clear_session(user_phone: str):
    """Clear a user's chat session."""
    try:
        success = chat_service.clear_session(user_phone)
        if success:
            return {"message": f"Session cleared for {user_phone}"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing session for {user_phone}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/sessions/all")
async def clear_all_sessions():
    """Clear all chat sessions."""
    try:
        # Get all sessions and clear them
        all_sessions = chat_service.session_storage.get_all_sessions()
        cleared_count = 0

        for user_phone in all_sessions.keys():
            if chat_service.clear_session(user_phone):
                cleared_count += 1

        return {
            "message": f"Cleared {cleared_count} sessions",
            "cleared_count": cleared_count
        }
    except Exception as e:
        logger.error(f"Error clearing all sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/send-message")
async def send_message(user_phone: str, message: str):
    """
    Send a message to a specific user (for testing purposes).

    Note: This endpoint is for testing only and should be disabled in production.
    """
    try:
        # Format phone number
        formatted_phone = twilio_service.format_phone_number(user_phone)

        # Send message via Twilio
        success = twilio_service.send_message(formatted_phone, message)

        if success:
            return {"message": f"Message sent to {user_phone}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message to {user_phone}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
