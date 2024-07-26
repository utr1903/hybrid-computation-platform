import redis


class RedisClient:
    def __init__(
        self,
        redis_master_server: str,
        redis_port: int,
        redis_password: str,
    ):
        self.client = redis.Redis(
            host=redis_master_server,
            port=redis_port,
            db=0,
            password=redis_password,
        )

    def set(
        self,
        key,
        value,
    ):
        self.client.set(key, value)

    def get(
        self,
        key,
    ):
        return self.client.get(key)
