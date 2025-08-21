from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from typing import Optional
from models import TwilioResponse
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwilioService:
    """Service class for Twilio WhatsApp interactions."""

    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.phone_number = settings.twilio_phone_number

    def send_message(self, to: str, body: str) -> bool:
        """
        Send a WhatsApp message via Twilio.

        Args:
            to: Recipient phone number (should include whatsapp: prefix)
            body: Message content

        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Ensure the 'to' number has the whatsapp: prefix
            if not to.startswith('whatsapp:'):
                to = f"whatsapp:{to}"

            # Send the message
            message = self.client.messages.create(
                from_=self.phone_number,
                body=body,
                to=to
            )

            logger.info(f"Message sent successfully. SID: {message.sid}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def create_twiml_response(self, message: str) -> str:
        """
        Create a TwiML response for webhook handling.

        Args:
            message: Response message content

        Returns:
            TwiML XML string
        """
        try:
            response = MessagingResponse()
            response.message(message)
            return str(response)

        except Exception as e:
            logger.error(f"Failed to create TwiML response: {e}")
            # Return a simple error response
            error_response = MessagingResponse()
            error_response.message("Sorry, I'm having trouble processing your message right now.")
            return str(error_response)

    def validate_webhook_signature(self, signature: str, url: str, params: dict) -> bool:
        """
        Validate Twilio webhook signature for security.

        Args:
            signature: X-Twilio-Signature header value
            url: Full webhook URL
            params: Request parameters

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(settings.twilio_auth_token)
            return validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False

    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number for WhatsApp.

        Args:
            phone: Raw phone number

        Returns:
            Formatted phone number with whatsapp: prefix
        """
        # Remove any existing whatsapp: prefix
        if phone.startswith('whatsapp:'):
            phone = phone[9:]

        # Remove any non-digit characters except +
        import re
        phone = re.sub(r'[^\d+]', '', phone)

        # Ensure it starts with +
        if not phone.startswith('+'):
            phone = '+' + phone

        return f"whatsapp:{phone}"
