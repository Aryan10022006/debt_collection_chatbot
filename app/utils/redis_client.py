import redis.asyncio as redis
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client for caching and session management"""
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.client = None

    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()

    async def set_session_data(self, session_token: str, data: dict, expire: int = 3600):
        """Store session data in Redis"""
        try:
            await self.client.setex(
                f"session:{session_token}",
                expire,
                json.dumps(data)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def get_session_data(self, session_token: str) -> dict:
        """Get session data from Redis"""
        try:
            data = await self.client.get(f"session:{session_token}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def cache_translation(self, text: str, from_lang: str, to_lang: str, translation: str):
        """Cache translation result"""
        try:
            cache_key = f"translation:{hash(text)}:{from_lang}:{to_lang}"
            await self.client.setex(cache_key, 86400, translation)  # 24 hours
        except Exception as e:
            logger.error(f"Translation cache error: {e}")

    async def get_cached_translation(self, text: str, from_lang: str, to_lang: str) -> str:
        """Get cached translation"""
        try:
            cache_key = f"translation:{hash(text)}:{from_lang}:{to_lang}"
            return await self.client.get(cache_key)
        except Exception as e:
            logger.error(f"Translation cache get error: {e}")
            return None

# Global instance
redis_client = RedisClient()
