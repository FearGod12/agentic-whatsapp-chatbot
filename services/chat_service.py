from typing import Dict, Optional, List
from models import ChatSession, OpenAIMessage
from services.openai_service import OpenAIService
from services.twilio_service import TwilioService
from services.session_storage import SessionStorage
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatService:
    """Service class for managing chat sessions and coordinating between Twilio and OpenAI."""

    def __init__(self):
        self.openai_service = OpenAIService()
        self.twilio_service = TwilioService()
        self.session_storage = SessionStorage()

    def get_or_create_session(self, user_phone: str) -> ChatSession:
        """
        Get existing session or create a new one for the user.

        Args:
            user_phone: User's phone number

        Returns:
            ChatSession object
        """
        # Clean up expired sessions
        self._cleanup_expired_sessions()

        # Try to get existing session from storage
        session_data = self.session_storage.get_session(user_phone)

        if session_data:
            # Reconstruct ChatSession from stored data
            session = ChatSession(
                user_phone=session_data['user_phone'],
                messages=[OpenAIMessage(**msg) for msg in session_data['messages']],
                created_at=session_data['created_at'],
                last_activity=session_data['last_activity']
            )
            logger.debug(f"Retrieved existing session for {user_phone}")
            return session
        else:
            # Create new session
            logger.info(f"Creating new chat session for {user_phone}")
            session = ChatSession(user_phone=user_phone)

            # Add system message to new session
            system_message = self.openai_service.create_system_message()
            session.add_message(system_message.role, system_message.content)

            # Save new session to storage
            self._save_session_to_storage(session)

            return session

    def _save_session_to_storage(self, session: ChatSession):
        """Save session to storage."""
        try:
            session_data = {
                'user_phone': session.user_phone,
                'messages': [msg.dict() for msg in session.messages],
                'created_at': session.created_at,
                'last_activity': session.last_activity
            }

            success = self.session_storage.save_session(session.user_phone, session_data)
            if success:
                logger.debug(f"Session saved successfully for {session.user_phone}")
            else:
                logger.warning(f"Failed to save session for {session.user_phone}")

        except Exception as e:
            logger.error(f"Error saving session for {session.user_phone}: {e}")

    async def process_message(self, user_phone: str, message: str) -> str:
        """
        Process incoming message and generate response.

        Args:
            user_phone: User's phone number
            message: Incoming message content

        Returns:
            Generated response message
        """
        try:
            # Get or create session
            session = self.get_or_create_session(user_phone)

            # Add user message to session
            session.add_message("user", message)

            # Get conversation history
            conversation_history = session.get_conversation_history()

            logger.info(f"Processing message for {user_phone}: {len(message)} characters")

            # Generate AI response
            ai_response = await self.openai_service.generate_response(
                messages=conversation_history,
                max_tokens=500,  # Keep responses concise for WhatsApp
                temperature=0.7
            )

            if ai_response:
                # Add AI response to session
                session.add_message("assistant", ai_response)

                # Save updated session to storage
                self._save_session_to_storage(session)

                logger.info(f"AI response generated for {user_phone}: {len(ai_response)} characters")
                return ai_response
            else:
                # Fallback response if AI fails
                fallback_response = "I'm sorry, I'm having trouble processing your message right now. Please try again in a moment."
                logger.warning(f"AI response generation failed for {user_phone}, using fallback")
                return fallback_response

        except Exception as e:
            logger.error(f"Error processing message for {user_phone}: {e}")
            return "I'm sorry, something went wrong. Please try again later."

    def _cleanup_expired_sessions(self):
        """Remove expired chat sessions to prevent memory leaks."""
        try:
            expired_count = self.session_storage.cleanup_expired_sessions()
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired sessions")
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")

    def get_session_info(self, user_phone: str) -> Optional[Dict]:
        """
        Get information about a user's chat session.

        Args:
            user_phone: User's phone number

        Returns:
            Session information dictionary or None if not found
        """
        try:
            session_data = self.session_storage.get_session(user_phone)
            if session_data:
                return {
                    "user_phone": session_data['user_phone'],
                    "message_count": len(session_data['messages']),
                    "created_at": session_data['created_at'].isoformat(),
                    "last_activity": session_data['last_activity'].isoformat(),
                    "is_active": datetime.now() - session_data['last_activity'] < timedelta(seconds=86400)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting session info for {user_phone}: {e}")
            return None

    def clear_session(self, user_phone: str) -> bool:
        """
        Clear a user's chat session.

        Args:
            user_phone: User's phone number

        Returns:
            True if session was cleared, False if not found
        """
        try:
            success = self.session_storage.delete_session(user_phone)
            if success:
                logger.info(f"Cleared chat session for {user_phone}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing session for {user_phone}: {e}")
            return False

    def get_active_sessions_count(self) -> int:
        """Get the number of active chat sessions."""
        try:
            self._cleanup_expired_sessions()
            all_sessions = self.session_storage.get_all_sessions()
            return len(all_sessions)
        except Exception as e:
            logger.error(f"Error getting active sessions count: {e}")
            return 0

    def get_storage_status(self) -> Dict:
        """Get storage status information."""
        try:
            return self.session_storage.get_storage_status()
        except Exception as e:
            logger.error(f"Error getting storage status: {e}")
            return {
                "storage_type": "unknown",
                "redis_connected": False,
                "error": str(e)
            }
