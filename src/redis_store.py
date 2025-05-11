import redis.asyncio as aioredis
from config import settings

JIT_EXPIRY = 3600

# Create Redis connection
async def get_redis_client():
    return aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password)

# Add JTI (JWT ID) to blocklist with expiration
async def add_jti_to_blocklist(jti: str):
    redis_client = await get_redis_client()
    await redis_client.set(name=jti, value="", ex=JIT_EXPIRY)

# Check if a JTI is in the blocklist
async def token_in_blocklist(jti: str) -> bool:
    redis_client = await get_redis_client()
    jti_value = await redis_client.get(jti)
    return jti_value is not None

store = aioredis.Redis(
  host=settings.redis_host,
  port=settings.redis_port,
  password=settings.redis_password
)