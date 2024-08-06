import os
import sys
import logging

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from pkg.config.config import Config
from pkg.server.server import Server
from commons.logger.logger import Logger
from commons.broker.kafkaproducer import BrokerProducerKafka


def main():

    # Parse config
    cfg = Config()
    if not cfg.validate():
        logging.error("Invalid configuration.")
        return

    # Set logger
    logger = Logger(level=cfg.LOGGING_LEVEL)

    # Create Kafka producer
    kafka = BrokerProducerKafka(
        bootstrapServers=cfg.BROKER_ADDRESS,
    )

    # Create & run HTTP server
    srv = Server(
        logger=logger,
        producer=kafka,
    )
    srv.run()


if __name__ == "__main__":
    main()
