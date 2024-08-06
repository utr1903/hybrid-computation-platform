import os
import sys
import logging
import multiprocessing

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from pkg.config.config import Config
from pkg.server.server import Server
from commons.logger.logger import Logger
from commons.broker.kafkaconsumer import BrokerConsumerKafka
from commons.database.mongodb import DatabaseMongoDb
from commons.cache.redis import CacheRedis
from pkg.tasks.taskscollectioncreator import (
    TasksCollectionCreator,
)
from pkg.tasks.taskcreator import BrokerProcessorTaskCreator
from pkg.tasks.taskupdator import BrokerProcessorTaskUpdator
from pkg.tasks.manager import TaskManager


def initializeTasksCollection(
    logLevel: str,
    databaseMasterAddress: str,
    databaseSlaveAddress: str,
    databaseUsername: str,
    databasePassword: str,
) -> bool:

    # Set logger
    logger = Logger(level=logLevel)

    # Create the tasks collection if it does not exist
    return TasksCollectionCreator(
        logger=logger,
        database=DatabaseMongoDb(
            masterAddress=databaseMasterAddress,
            slaveAddress=databaseSlaveAddress,
            username=databaseUsername,
            password=databasePassword,
        ),
    ).run()


def processTasksRequests(
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

    # Instantiate broker processor for creating tasks
    brokerProcessorTaskCreator = BrokerProcessorTaskCreator(
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
            topic="jobsubmitted",
            consumerGroupId="tasksmanager",
        ),
    )

    # Instantiate broker processor for updating tasks
    brokerProcessorTaskUpdator = BrokerProcessorTaskUpdator(
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
            topic="taskupdated",
            consumerGroupId="tasksmanager",
        ),
    )

    # Run the job creator
    TaskManager(
        brokerProcessors=[
            brokerProcessorTaskCreator,
            brokerProcessorTaskUpdator,
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
        exit(1)

    # Create the tasks collection if it does not exist
    if not initializeTasksCollection(
        cfg.LOGGING_LEVEL,
        cfg.DATABASE_MASTER_ADDRESS,
        cfg.DATABASE_SLAVE_ADDRESS,
        cfg.DATABASE_USERNAME,
        cfg.DATABASE_PASSWORD,
    ):
        exit(1)

    processes: list[multiprocessing.Process] = []
    processes.append(
        multiprocessing.Process(
            target=processTasksRequests,
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
