import os
import sys
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from pkg.config.config import Config
from pkg.server.server import Server
from commons.database.mongodb import DatabaseMongoDb
from commons.cache.redis import CacheRedis


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

    # Instantiate MongoDB database
    mongodb = DatabaseMongoDb(
        slaveAddress=cfg.DATABASE_SLAVE_ADDRESS,
        username=cfg.DATABASE_USERNAME,
        password=cfg.DATABASE_PASSWORD,
    )
    mongodb.connect()

    # Instantiate Redis cache
    redis = CacheRedis(
        masterAddress=cfg.CACHE_MASTER_ADDRESS,
        slaveAddress=cfg.CACHE_SLAVE_ADDRESS,
        port=int(cfg.CACHE_PORT),
        password=cfg.CACHE_PASSWORD,
    )
    redis.connect()

    # Create & run HTTP server
    srv = Server(
        database=mongodb,
        cache=redis,
    )
    srv.run()


if __name__ == "__main__":
    main()
