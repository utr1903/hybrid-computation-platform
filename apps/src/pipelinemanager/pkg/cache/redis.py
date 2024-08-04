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
        self.masterAddress = masterAddress
        self.slaveAddress = slaveAddress
        self.port = port
        self.password = password

    def connect(
        self,
    ) -> None:
        self.master = redis.Redis(
            host=self.masterAddress,
            port=self.port,
            db=0,
            password=self.password,
        )

        self.slave = redis.Redis(
            host=self.slaveAddress,
            port=self.port,
            db=0,
            password=self.password,
        )

    def set(
        self,
        key,
        value,
    ) -> None:
        self.master.set(key, value)
