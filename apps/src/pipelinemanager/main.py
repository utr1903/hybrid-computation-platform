import os
import sys
import logging
import multiprocessing

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from pkg.config.config import Config
from pkg.server.server import Server
from commons.broker.kafkaproducer import BrokerProducerKafka
from commons.broker.kafkaconsumer import BrokerConsumerKafka
from commons.database.mongodb import DatabaseMongoDb
from commons.cache.redis import CacheRedis
from pkg.pipelines.pipelinecollectioncreator import (
    PipelineCollectionCreator,
)
from pkg.pipelines.taskcreator import BrokerProcessorTaskCreator
from pkg.pipelines.taskupdator import BrokerProcessorTaskUpdator
from pkg.pipelines.manager import TaskManager


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


def initializePipelinesCollection(
    databaseMasterAddress: str,
    databaseSlaveAddress: str,
    databaseUsername: str,
    databasePassword: str,
) -> bool:

    # Create the pipelines collection if it does not exist
    return PipelineCollectionCreator(
        database=DatabaseMongoDb(
            masterAddress=databaseMasterAddress,
            slaveAddress=databaseSlaveAddress,
            username=databaseUsername,
            password=databasePassword,
        ),
    ).run()


def processPipelineRequests(
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
    # Instantiate broker processor for creating tasks
    brokerProcessorTaskCreator = BrokerProcessorTaskCreator(
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
            consumerGroupId="pipelinemanager",
        ),
    )

    # Instantiate broker processor for updating tasks
    brokerProcessorTaskUpdator = BrokerProcessorTaskUpdator(
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
            consumerGroupId="pipelinemanager",
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

    # Set logging level
    setLoggingLevel(level=cfg.LOGGING_LEVEL)

    # Create the pipelines collection if it does not exist
    if not initializePipelinesCollection(
        cfg.DATABASE_MASTER_ADDRESS,
        cfg.DATABASE_SLAVE_ADDRESS,
        cfg.DATABASE_USERNAME,
        cfg.DATABASE_PASSWORD,
    ):
        exit(1)

    processes: list[multiprocessing.Process] = []
    processes.append(
        multiprocessing.Process(
            target=processPipelineRequests,
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
