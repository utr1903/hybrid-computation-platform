import os
import sys
import logging
import multiprocessing

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from pkg.config.config import Config
from pkg.server.server import Server
from commons.logger.logger import Logger
from commons.broker.kafkaproducer import BrokerProducerKafka
from commons.broker.kafkaconsumer import BrokerConsumerKafka
from commons.database.mongodb import DatabaseMongoDb
from commons.cache.redis import CacheRedis
from pkg.jobs.brokerprocessorjobscollectioncreator import (
    BrokerProcessorJobsCollectionCreator,
)
from pkg.jobs.brokerprocessorjobcreator import BrokerProcessorJobCreator
from pkg.jobs.brokerprocessorjobupdator import BrokerProcessorJobUpdator
from pkg.jobs.manager import JobManager


def processJobRequests(
    logLevel: str,
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

    # Set logger
    logger = Logger(level=logLevel)

    # Instantiate broker processor for creating job collections
    brokerProcessorJobsCollectionCreator = BrokerProcessorJobsCollectionCreator(
        logger=logger,
        database=DatabaseMongoDb(
            masterAddress=databaseMasterAddress,
            slaveAddress=databaseSlaveAddress,
            username=databaseUsername,
            password=databasePassword,
        ),
        cache=CacheRedis(
            masterAddress=cacheMasterAddress,
            slaveAddress=cacheSlaveAddress,
            port=int(cachePort),
            password=cachePassword,
        ),
        brokerConsumer=BrokerConsumerKafka(
            bootstrapServers=brokerAddress,
            topic="organizationcreated",
            consumerGroupId="jobmanager",
        ),
    )

    # Instantiate broker processor for creating jobs
    brokerProcessorJobCreator = BrokerProcessorJobCreator(
        logger=logger,
        database=DatabaseMongoDb(
            masterAddress=databaseMasterAddress,
            slaveAddress=databaseSlaveAddress,
            username=databaseUsername,
            password=databasePassword,
        ),
        cache=CacheRedis(
            masterAddress=cacheMasterAddress,
            slaveAddress=cacheSlaveAddress,
            port=int(cachePort),
            password=cachePassword,
        ),
        brokerConsumer=BrokerConsumerKafka(
            bootstrapServers=brokerAddress,
            topic="createjob",
            consumerGroupId="jobmanager",
        ),
    )

    # Instantiate broker processor for creating jobs
    brokerProcessorJobUpdator = BrokerProcessorJobUpdator(
        logger=logger,
        database=DatabaseMongoDb(
            masterAddress=databaseMasterAddress,
            slaveAddress=databaseSlaveAddress,
            username=databaseUsername,
            password=databasePassword,
        ),
        cache=CacheRedis(
            masterAddress=cacheMasterAddress,
            slaveAddress=cacheSlaveAddress,
            port=int(cachePort),
            password=cachePassword,
        ),
        brokerConsumer=BrokerConsumerKafka(
            bootstrapServers=brokerAddress,
            topic="updatejob",
            consumerGroupId="jobmanager",
        ),
        brokerProducer=BrokerProducerKafka(
            bootstrapServers=brokerAddress,
        ),
    )

    # Run the job creator
    JobManager(
        brokerProcessors=[
            brokerProcessorJobsCollectionCreator,
            brokerProcessorJobCreator,
            brokerProcessorJobUpdator,
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

    processes: list[multiprocessing.Process] = []
    processes.append(
        multiprocessing.Process(
            target=processJobRequests,
            args=(
                cfg.LOGGING_LEVEL,
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
