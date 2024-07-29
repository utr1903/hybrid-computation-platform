import redis

from pkg.cache.cache import Cache


class CacheRedis(Cache):

    def __init__(
        self,
        masterAddress: str,
        slaveAddress: str,
        port: int,
        password: str,
    ):
        self.master = redis.Redis(
            host=masterAddress,
            port=port,
            db=0,
            password=password,
        )

        self.slave = redis.Redis(
            host=slaveAddress,
            port=port,
            db=0,
            password=password,
        )

    def set(
        self,
        key,
        value,
    ) -> None:
        self.master.set(key, value)

    def get(
        self,
        key,
    ) -> bytes | None:
        return self.slave.get(key)
