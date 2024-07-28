import redis


class RedisClient:
    def __init__(
        self,
        redis_master_server: str,
        redis_slave_servers: str,
        redis_port: int,
        redis_password: str,
    ):
        self.master = redis.Redis(
            host=redis_master_server,
            port=redis_port,
            db=0,
            password=redis_password,
        )

        self.slave = redis.Redis(
            host=redis_slave_servers,
            port=redis_port,
            db=0,
            password=redis_password,
        )

    def set(
        self,
        key,
        value,
    ):
        self.master.set(key, value)

    def get(
        self,
        key,
    ):
        return self.slave.get(key)
