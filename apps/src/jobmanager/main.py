import logging

from pkg.config.config import Config
from pkg.server.server import Server
from pkg.redis.client import RedisClient


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

    cache = RedisClient(
        redis_master_server=cfg.REDIS_MASTER_SERVER,
        redis_slave_servers=cfg.REDIS_SLAVES_SERVERS,
        redis_port=cfg.REDIS_PORT,
        redis_password=cfg.REDIS_PASSWORD,
    )
    # Create & run HTTP server
    srv = Server(
        cache=cache,
    )
    srv.run()


if __name__ == "__main__":
    main()
