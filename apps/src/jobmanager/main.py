import logging

from pkg.config.config import Config
from pkg.server.server import Server
from pkg.cache.redis import CacheRedis


def setLoggingLevel(
    level,
):
    if level == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif level == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif level == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)


def main():

    # Parse config
    cfg = Config()
    if not cfg.validate():
        logging.error("Invalid configuration.")
        return

    # Set logging level
    setLoggingLevel(level=cfg.LOGGING_LEVEL)

    # Instantiate Redis cache
    redis = CacheRedis(
        masterAddress=cfg.REDIS_MASTER_SERVER,
        slaveAddress=cfg.REDIS_SLAVES_SERVERS,
        port=int(cfg.REDIS_PORT),
        password=cfg.REDIS_PASSWORD,
    )

    # Create & run HTTP server
    srv = Server(
        cache=redis,
    )
    srv.run()


if __name__ == "__main__":
    main()
