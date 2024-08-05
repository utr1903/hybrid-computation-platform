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
from pkg.organizations.organizationcollectioncreator import (
    OrganizationCollectionCreator,
)
from pkg.organizations.organizationcreator import OrganizationCreator


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


def initializeOrganizationsCollection(
    databaseMasterAddress: str,
    databaseSlaveAddress: str,
    databaseUsername: str,
    databasePassword: str,
) -> bool:

    mongodb = DatabaseMongoDb(
        masterAddress=databaseMasterAddress,
        slaveAddress=databaseSlaveAddress,
        username=databaseUsername,
        password=databasePassword,
    )

    # Create the organizations collection if it does not exist
    return OrganizationCollectionCreator(
        database=mongodb,
    ).run()


def processOrganizationRequests(
    databaseMasterAddress: str,
    databaseSlaveAddress: str,
    databaseUsername: str,
    databasePassword: str,
    brokerAddress: str,
    brokerConsumerGroup: str,
):
    # Instantiate MongoDB database
    mongodb = DatabaseMongoDb(
        masterAddress=databaseMasterAddress,
        slaveAddress=databaseSlaveAddress,
        username=databaseUsername,
        password=databasePassword,
    )

    # Instantiate Kafka producer
    kafkaProducer = BrokerProducerKafka(
        bootstrapServers=brokerAddress,
    )

    # Instantiate Kafka consumer
    kafkaConsumer = BrokerConsumerKafka(
        bootstrapServers=brokerAddress,
        consumerGroupId=brokerConsumerGroup,
    )

    # Run the job creator
    OrganizationCreator(
        database=mongodb,
        brokerProducer=kafkaProducer,
        brokerConsumer=kafkaConsumer,
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

    # Create the organizations collection if it does not exist
    if not initializeOrganizationsCollection(
        cfg.DATABASE_MASTER_ADDRESS,
        cfg.DATABASE_SLAVE_ADDRESS,
        cfg.DATABASE_USERNAME,
        cfg.DATABASE_PASSWORD,
    ):
        exit(1)

    processes: list[multiprocessing.Process] = []
    processes.append(
        multiprocessing.Process(
            target=processOrganizationRequests,
            args=(
                cfg.DATABASE_MASTER_ADDRESS,
                cfg.DATABASE_SLAVE_ADDRESS,
                cfg.DATABASE_USERNAME,
                cfg.DATABASE_PASSWORD,
                cfg.BROKER_ADDRESS,
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
