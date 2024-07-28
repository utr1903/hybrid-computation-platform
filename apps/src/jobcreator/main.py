import logging
import multiprocessing

from pkg.config.config import Config
from pkg.server.server import Server
from pkg.broker.kafkaconsumer import BrokerConsumerKafka
from pkg.cache.redis import CacheRedis
from pkg.jobs.creator import JobCreator


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


def processJobRequests(
    cacheMasterAddress: str,
    cacheSlaveAddress: str,
    cachePort: str,
    cachePassword: str,
    brokerAddress: str,
    brokerTopic: str,
    brokerConsumerGroup: str,
):
    # Instantiate Redis cache
    redis = CacheRedis(
        masterAddress=cacheMasterAddress,
        slaveAddress=cacheSlaveAddress,
        port=int(cachePort),
        password=cachePassword,
    )

    # Instantiate Kafka consumer
    kafkaConsumer = BrokerConsumerKafka(
        bootstrapServers=brokerAddress,
        topic=brokerTopic,
        consumerGroupId=brokerConsumerGroup,
    )

    # Run the job creator
    JobCreator(
        brokerConsumer=kafkaConsumer,
        cache=redis,
    ).run()


def startServer():
    server = Server()
    server.run()


def main():

    # Parse config
    cfg = Config()
    if not cfg.validate():
        logging.error("Invalid configuration.")
        return

    # Set logging level
    setLoggingLevel(level=cfg.LOGGING_LEVEL)

    processes: list[multiprocessing.Process] = []
    processes.append(
        multiprocessing.Process(
            target=processJobRequests,
            args=(
                cfg.CACHE_MASTER_ADDRESS,
                cfg.CACHE_SLAVE_ADDRESS,
                cfg.CACHE_PORT,
                cfg.CACHE_PASSWORD,
                cfg.BROKER_ADDRESS,
                cfg.BROKER_TOPIC,
                cfg.BROKER_CONSUMER_GROUP,
            ),
        )
    )
    processes.append(
        multiprocessing.Process(
            target=startServer,
        )
    )

    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
