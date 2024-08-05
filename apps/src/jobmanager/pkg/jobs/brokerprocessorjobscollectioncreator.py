import json
import logging

from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.jobs import OrganizationDataObject
from pkg.jobs.brokerprocessor import BrokerProcessor

logger = logging.getLogger(__name__)


class BrokerProcessorJobsCollectionCreator(BrokerProcessor):
    def __init__(
        self,
        database: Database,
        cache: Cache,
        brokerConsumer: BrokerConsumer,
    ):
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
            logger.info(message)

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
                logger.warning(
                    f"Collection [jobs] in database [{organizationDataObject.organizationId}] already exists."
                )

        except Exception as e:
            logger.error(f"Error processing jobs collection creation: {e}")

    def parseMessage(
        self,
        message,
    ) -> dict:

        logger.info("Parsing message...")

        try:
            messageParsed = json.loads(message)
        except Exception as e:
            logger.error(e)
            raise Exception("Message parsing failed: {e}")

        self.validateMessage(messageParsed)

        return messageParsed

    def validateMessage(
        self,
        messageParsed,
    ) -> None:

        logger.info("Validating message...")

        missingFields = []
        if "organizationId" not in messageParsed:
            missingFields.append("organizationId")

        if "organizationName" not in messageParsed:
            missingFields.append("organizationName")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message validation succeeded.")

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

        logger.info(f"Collection [{collectionName}] does not exist. Creating...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="jobId",
            isUnique=True,
        )
        logger.info(f"Creating collection [{collectionName}] succeeded.")
