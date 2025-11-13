import redis.asyncio as aioredis
from app.config import settings

redis_client: aioredis.Redis = None

async def connect_redis():
    """
    Connects to the Redis server.
    """
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await redis_client.ping()

async def close_redis():
    """
    Closes the Redis connection.
    """
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_redis_client() -> aioredis.Redis:
    """
    Dependency that provides an async Redis client.
    """
    if not redis_client:
        await connect_redis()
    return redis_client
