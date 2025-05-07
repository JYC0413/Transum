import os
import redis
from dotenv import load_dotenv
from redis.connection import ConnectionPool

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', 56))

# 创建 Redis 连接池
redis_pool = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    max_connections=MAX_CONNECTIONS,  # Adjust based on your concurrency needs
    decode_responses=True
)

redis_conn = redis.Redis(connection_pool=redis_pool)

connectionError = redis.ConnectionError
