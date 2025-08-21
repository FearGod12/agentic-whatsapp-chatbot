from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TwilioWebhookRequest(BaseModel):
    """Model for incoming Twilio webhook requests."""
    message_sid: str = Field(..., alias="MessageSid")
    from_: str = Field(..., alias="From")
    to: str = Field(..., alias="To")
    body: str = Field(..., alias="Body")
    num_media: Optional[str] = Field(None, alias="NumMedia")
    media_url: Optional[str] = Field(None, alias="MediaUrl0")
    timestamp: Optional[str] = Field(None, alias="MessageTimestamp")

    class Config:
        allow_population_by_field_name = True


class TwilioResponse(BaseModel):
    """Model for Twilio TwiML response."""
    message: str
    media_url: Optional[str] = None


class OpenAIMessage(BaseModel):
    """Model for OpenAI API message format."""
    role: str
    content: str


class OpenAIRequest(BaseModel):
    """Model for OpenAI API request."""
    model: str
    messages: List[OpenAIMessage]
    max_tokens: int = 1000
    temperature: float = 0.7


class OpenAIResponse(BaseModel):
    """Model for OpenAI API response."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class ChatSession(BaseModel):
    """Model for chat session management."""
    user_phone: str
    messages: List[OpenAIMessage] = []
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        """Add a message to the session."""
        self.messages.append(OpenAIMessage(role=role, content=content))
        self.last_activity = datetime.now()

    def get_conversation_history(self, max_messages: int = 10) -> List[OpenAIMessage]:
        """Get recent conversation history."""
        return self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages


class HealthCheck(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
