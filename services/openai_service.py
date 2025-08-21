import openai
from typing import List, Optional
from models import OpenAIMessage, OpenAIRequest, OpenAIResponse
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure OpenAI client
openai.api_key = settings.openai_api_key


class OpenAIService:
    """Service class for OpenAI API interactions."""

    def __init__(self):
        self.model = settings.openai_model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def generate_response(
        self,
        messages: List[OpenAIMessage],
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate a response using OpenAI API.

        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens for response
            temperature: Response creativity (0.0 to 1.0)

        Returns:
            Generated response text or None if error
        """
        try:
            # Prepare the request
            request_data = {
                "model": self.model,
                "messages": [msg.dict() for msg in messages],
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            logger.info(f"Making OpenAI API request with {len(messages)} messages")

            # Make the API call
            response = self.client.chat.completions.create(**request_data)

            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                logger.info(f"OpenAI response generated successfully: {len(content)} characters")
                return content
            else:
                logger.error("OpenAI response contained no choices")
                return None

        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed. Check your API key.")
            return None
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded. Please try again later.")
            return None
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI service: {e}")
            return None

    def create_system_message(self) -> OpenAIMessage:
        """Create a system message to define the bot's behavior."""
        system_prompt = """You are a helpful and friendly WhatsApp chatbot assistant.
        You should be conversational, concise, and helpful.
        Keep responses under 500 characters when possible, as this is for WhatsApp messaging.
        Be polite, professional, and engaging in your responses."""

        return OpenAIMessage(role="system", content=system_prompt)

    def create_user_message(self, content: str) -> OpenAIMessage:
        """Create a user message."""
        return OpenAIMessage(role="user", content=content)

    def create_assistant_message(self, content: str) -> OpenAIMessage:
        """Create an assistant message."""
        return OpenAIMessage(role="assistant", content=content)
