import json
import pickle
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from redis import Redis, ConnectionError, TimeoutError
from config import settings

logger = logging.getLogger(__name__)


class SessionStorage:
    """Session storage service with Redis primary and in-memory fallback."""

    def __init__(self):
        self.redis_client = None
        self.fallback_storage: Dict[str, Any] = {}
        self.use_redis = False
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection with fallback to in-memory storage."""
        try:
            if settings.redis_password:
                self.redis_client = Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    ssl=settings.redis_use_ssl,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                self.redis_client = Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    ssl=settings.redis_use_ssl,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

            # Test Redis connection
            self.redis_client.ping()
            self.use_redis = True
            logger.info("✅ Redis connection established successfully")

        except (ConnectionError, TimeoutError, Exception) as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            logger.info("🔄 Falling back to in-memory storage")
            self.use_redis = False
            self.redis_client = None

    def _get_redis_key(self, user_phone: str) -> str:
        """Generate Redis key for user session."""
        return f"whatsapp_session:{user_phone}"

    def _serialize_session(self, session_data: Dict[str, Any]) -> str:
        """Serialize session data to JSON string."""
        # Convert datetime objects to ISO format for JSON serialization
        serializable_data = session_data.copy()
        if 'created_at' in serializable_data:
            serializable_data['created_at'] = serializable_data['created_at'].isoformat()
        if 'last_activity' in serializable_data:
            serializable_data['last_activity'] = serializable_data['last_activity'].isoformat()

        return json.dumps(serializable_data)

    def _deserialize_session(self, session_json: str) -> Dict[str, Any]:
        """Deserialize session data from JSON string."""
        session_data = json.loads(session_json)

        # Convert ISO format strings back to datetime objects
        if 'created_at' in session_data:
            session_data['created_at'] = datetime.fromisoformat(session_data['created_at'])
        if 'last_activity' in session_data:
            session_data['last_activity'] = datetime.fromisoformat(session_data['last_activity'])

        return session_data

    def get_session(self, user_phone: str) -> Optional[Dict[str, Any]]:
        """
        Get session data for a user.

        Args:
            user_phone: User's phone number

        Returns:
            Session data dictionary or None if not found
        """
        try:
            if self.use_redis and self.redis_client:
                # Try Redis first
                redis_key = self._get_redis_key(user_phone)
                session_json = self.redis_client.get(redis_key)

                if session_json:
                    session_data = self._deserialize_session(session_json)
                    logger.debug(f"Retrieved session from Redis for {user_phone}")
                    return session_data
                else:
                    # Check fallback storage
                    if user_phone in self.fallback_storage:
                        logger.debug(f"Retrieved session from fallback storage for {user_phone}")
                        return self.fallback_storage[user_phone]
                    return None
            else:
                # Use fallback storage
                if user_phone in self.fallback_storage:
                    logger.debug(f"Retrieved session from fallback storage for {user_phone}")
                    return self.fallback_storage[user_phone]
                return None

        except Exception as e:
            logger.error(f"Error retrieving session for {user_phone}: {e}")
            # Fallback to in-memory storage
            if user_phone in self.fallback_storage:
                logger.debug(f"Retrieved session from fallback storage after error for {user_phone}")
                return self.fallback_storage[user_phone]
            return None

    def save_session(self, user_phone: str, session_data: Dict[str, Any]) -> bool:
        """
        Save session data for a user.

        Args:
            user_phone: User's phone number
            session_data: Session data to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Always save to fallback storage as backup
            self.fallback_storage[user_phone] = session_data.copy()

            if self.use_redis and self.redis_client:
                # Try to save to Redis
                redis_key = self._get_redis_key(user_phone)
                session_json = self._serialize_session(session_data)

                # Save with TTL
                success = self.redis_client.setex(
                    redis_key,
                    settings.session_ttl,
                    session_json
                )

                if success:
                    logger.debug(f"Saved session to Redis for {user_phone}")
                    return True
                else:
                    logger.warning(f"Failed to save session to Redis for {user_phone}")
                    return False
            else:
                # Only fallback storage
                logger.debug(f"Saved session to fallback storage for {user_phone}")
                return True

        except Exception as e:
            logger.error(f"Error saving session for {user_phone}: {e}")
            # Session is still saved in fallback storage
            return True

    def delete_session(self, user_phone: str) -> bool:
        """
        Delete session data for a user.

        Args:
            user_phone: User's phone number

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Remove from fallback storage
            if user_phone in self.fallback_storage:
                del self.fallback_storage[user_phone]

            if self.use_redis and self.redis_client:
                # Try to delete from Redis
                redis_key = self._get_redis_key(user_phone)
                deleted = self.redis_client.delete(redis_key)

                if deleted:
                    logger.debug(f"Deleted session from Redis for {user_phone}")
                else:
                    logger.debug(f"Session not found in Redis for {user_phone}")

                return True
            else:
                logger.debug(f"Deleted session from fallback storage for {user_phone}")
                return True

        except Exception as e:
            logger.error(f"Error deleting session for {user_phone}: {e}")
            return False

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions (for monitoring purposes).

        Returns:
            Dictionary of all active sessions
        """
        try:
            if self.use_redis and self.redis_client:
                # Get all session keys from Redis
                pattern = "whatsapp_session:*"
                keys = self.redis_client.keys(pattern)

                sessions = {}
                for key in keys:
                    user_phone = key.replace("whatsapp_session:", "")
                    session_data = self.get_session(user_phone)
                    if session_data:
                        sessions[user_phone] = session_data

                return sessions
            else:
                # Return fallback storage
                return self.fallback_storage.copy()

        except Exception as e:
            logger.error(f"Error getting all sessions: {e}")
            return self.fallback_storage.copy()

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        try:
            current_time = datetime.now()
            expired_count = 0

            if self.use_redis and self.redis_client:
                # Redis handles TTL automatically, but we can clean up fallback storage
                expired_sessions = []

                for user_phone, session_data in self.fallback_storage.items():
                    if 'last_activity' in session_data:
                        last_activity = session_data['last_activity']
                        if isinstance(last_activity, str):
                            last_activity = datetime.fromisoformat(last_activity)

                        if current_time - last_activity > timedelta(seconds=settings.session_ttl):
                            expired_sessions.append(user_phone)

                # Remove expired sessions from fallback storage
                for user_phone in expired_sessions:
                    del self.fallback_storage[user_phone]
                    expired_count += 1

                logger.info(f"Cleaned up {expired_count} expired sessions from fallback storage")
            else:
                # Clean up fallback storage
                expired_sessions = []

                for user_phone, session_data in self.fallback_storage.items():
                    if 'last_activity' in session_data:
                        last_activity = session_data['last_activity']
                        if isinstance(last_activity, str):
                            last_activity = datetime.fromisoformat(last_activity)

                        if current_time - last_activity > timedelta(seconds=settings.session_ttl):
                            expired_sessions.append(user_phone)

                # Remove expired sessions
                for user_phone in expired_sessions:
                    del self.fallback_storage[user_phone]
                    expired_count += 1

                logger.info(f"Cleaned up {expired_count} expired sessions from fallback storage")

            return expired_count

        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    def get_storage_status(self) -> Dict[str, Any]:
        """
        Get storage status information.

        Returns:
            Dictionary with storage status information
        """
        try:
            status = {
                "storage_type": "redis" if self.use_redis else "in_memory",
                "redis_connected": self.use_redis,
                "fallback_storage_count": len(self.fallback_storage)
            }

            if self.use_redis and self.redis_client:
                try:
                    # Get Redis info
                    redis_info = self.redis_client.info()
                    status.update({
                        "redis_memory_used": redis_info.get("used_memory_human", "N/A"),
                        "redis_connected_clients": redis_info.get("connected_clients", 0),
                        "redis_uptime": redis_info.get("uptime_in_seconds", 0)
                    })
                except Exception as e:
                    status["redis_info_error"] = str(e)

            return status

        except Exception as e:
            logger.error(f"Error getting storage status: {e}")
            return {
                "storage_type": "unknown",
                "redis_connected": False,
                "error": str(e)
            }
