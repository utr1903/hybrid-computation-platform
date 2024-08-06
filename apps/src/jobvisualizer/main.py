import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from pkg.config.config import Config
from pkg.server.server import Server
from commons.logger.logger import Logger
from commons.database.mongodb import DatabaseMongoDb
from commons.cache.redis import CacheRedis


def main():

    # Parse config
    cfg = Config()
    if not cfg.validate():
        print("Invalid configuration.")
        exit(1)

    # Set logger
    logger = Logger(level=cfg.LOGGING_LEVEL)

    # Instantiate MongoDB database
    mongodb = DatabaseMongoDb(
        masterAddress=cfg.DATABASE_MASTER_ADDRESS,
        slaveAddress=cfg.DATABASE_SLAVE_ADDRESS,
        username=cfg.DATABASE_USERNAME,
        password=cfg.DATABASE_PASSWORD,
    )

    # Instantiate Redis cache
    redis = CacheRedis(
        masterAddress=cfg.CACHE_MASTER_ADDRESS,
        slaveAddress=cfg.CACHE_SLAVE_ADDRESS,
        port=int(cfg.CACHE_PORT),
        password=cfg.CACHE_PASSWORD,
    )

    # Create & run HTTP server
    srv = Server(
        logger=logger,
        database=mongodb,
        cache=redis,
    )
    srv.run()


if __name__ == "__main__":
    main()
