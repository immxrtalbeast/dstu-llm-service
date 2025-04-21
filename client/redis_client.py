import redis

# Настрой по своему адресу/паролю, если нужно
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
)
