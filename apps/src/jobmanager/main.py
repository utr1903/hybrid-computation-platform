import logging
import multiprocessing

from pkg.config.config import Config
from pkg.server.server import Server
from pkg.broker.kafkaconsumer import BrokerConsumerKafka
from pkg.database.mongodb import DatabaseMongoDb
from pkg.cache.redis import CacheRedis
from pkg.jobs.brokerprocessorjobcreator import BrokerProcessorJobCreator
from pkg.jobs.brokerprocessorjobscollectioncreator import (
    BrokerProcessorJobsCollectionCreator,
)
from pkg.jobs.manager import JobManager


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
    databaseMasterAddress: str,
    databaseSlaveAddress: str,
    databaseUsername: str,
    databasePassword: str,
    cacheMasterAddress: str,
    cacheSlaveAddress: str,
    cachePort: str,
    cachePassword: str,
    brokerAddress: str,
):
    # Instantiate MongoDB database
    mongodb = DatabaseMongoDb(
        masterAddress=databaseMasterAddress,
        slaveAddress=databaseSlaveAddress,
        username=databaseUsername,
        password=databasePassword,
    )

    # Instantiate Redis cache
    redis = CacheRedis(
        masterAddress=cacheMasterAddress,
        slaveAddress=cacheSlaveAddress,
        port=int(cachePort),
        password=cachePassword,
    )

    # Instantiate broker processor for creating job collections
    brokerProcessorJobsCollectionCreator = BrokerProcessorJobsCollectionCreator(
        database=mongodb,
        cache=redis,
        brokerConsumer=BrokerConsumerKafka(
            bootstrapServers=brokerAddress,
            topic="organizationcreated",
            consumerGroupId="jobmanager",
        ),
    )

    # Instantiate broker processor for creating jobs
    brokerProcessorJobCreator = BrokerProcessorJobCreator(
        database=mongodb,
        cache=redis,
        brokerConsumer=BrokerConsumerKafka(
            bootstrapServers=brokerAddress,
            topic="createjob",
            consumerGroupId="jobmanager",
        ),
    )

    # Run the job creator
    JobManager(
        brokerProcessors=[
            brokerProcessorJobsCollectionCreator,
            brokerProcessorJobCreator,
        ],
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
                cfg.DATABASE_MASTER_ADDRESS,
                cfg.DATABASE_SLAVE_ADDRESS,
                cfg.DATABASE_USERNAME,
                cfg.DATABASE_PASSWORD,
                cfg.CACHE_MASTER_ADDRESS,
                cfg.CACHE_SLAVE_ADDRESS,
                cfg.CACHE_PORT,
                cfg.CACHE_PASSWORD,
                cfg.BROKER_ADDRESS,
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
