import json
import logging

from commons.logger.logger import Logger
from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.jobs import OrganizationDataObject
from pkg.jobs.brokerprocessor import BrokerProcessor


class BrokerProcessorJobsCollectionCreator(BrokerProcessor):
    def __init__(
        self,
        logger: Logger,
        database: Database,
        cache: Cache,
        brokerConsumer: BrokerConsumer,
    ):
        self.logger = logger
        self.database = database
        self.cache = cache
        self.brokerConsumer = brokerConsumer

    def run(
        self,
    ) -> None:
        # Establish connections
        self.establishConnections()

        # Consume messages
        self.brokerConsumer.consume(
            self.processJobsCollectionCreateRequest,
        )

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.cache.connect()
        self.brokerConsumer.connect()

    def processJobsCollectionCreateRequest(
        self,
        message,
    ) -> None:

        try:
            # Parse message
            messageParsed = self.parseMessage(message)

            # Extract organization data object
            organizationDataObject = self.extractOrganizationDataObject(messageParsed)

            # Check if the jobs collection for the organization exists
            collectionExists = self.doesCollectionExist(
                organizationDataObject.organizationId,
            )

            # Create the jobs collection if it does not exist
            if not collectionExists:
                self.createCollection(
                    organizationDataObject.organizationId,
                )
            else:
                self.logger.log(
                    logging.WARNING,
                    f"Collection [jobs] in database [{organizationDataObject.organizationId}] already exists.",
                )

        except Exception as e:
            self.logger.log(
                logging.ERROR,
                f"Error processing jobs collection creation.",
                attrs={"error": str(e)},
            )

    def parseMessage(
        self,
        message,
    ) -> dict:

        self.logger.log(
            logging.INFO,
            "Parsing message...",
        )

        try:
            messageParsed = json.loads(message)
        except Exception as e:
            self.logger.log(
                logging.ERROR,
                "Message parsing failed.",
                attrs={"error": str(e)},
            )
            raise Exception("Message parsing failed: {e}")

        self.validateMessage(messageParsed)

        return messageParsed

    def validateMessage(
        self,
        messageParsed,
    ) -> None:

        self.logger.log(
            logging.INFO,
            "Validating message...",
        )

        missingFields = []
        if "organizationId" not in messageParsed:
            missingFields.append("organizationId")

        if "organizationName" not in messageParsed:
            missingFields.append("organizationName")

        if len(missingFields) > 0:
            msg = "There are missing fields which have to be defined."
            self.logger.log(
                logging.ERROR,
                msg,
                attrs={
                    "missingFields": ",".join(map(str, missingFields)),
                },
            )
            raise Exception(msg)

        self.logger.log(
            logging.INFO,
            "Message validation succeeded.",
        )

    def extractOrganizationDataObject(
        self,
        message: dict,
    ) -> OrganizationDataObject:

        return OrganizationDataObject(
            organizationId=message.get("organizationId"),
            organizationName=message.get("organizationName"),
        )

    def doesCollectionExist(
        self,
        databaseName: str,
    ):
        return self.database.doesCollectionExist(
            databaseName=databaseName,
            collectionName="jobs",
        )

    def createCollection(
        self,
        databaseName: str,
    ):
        collectionName = "jobs"

        self.logger.log(
            logging.INFO,
            f"Collection [{collectionName}] does not exist. Creating...",
        )
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="jobId",
            isUnique=True,
        )
        self.logger.log(
            logging.INFO,
            f"Creating collection [{collectionName}] succeeded.",
        )
