import logging

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from pkg.data.jobs import OrganizationDataObject

logger = logging.getLogger(__name__)


class JobsCollectionCreator:
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
        topic,
    ) -> None:

        self.brokerConsumer.consume(
            topic,
            self.processJobsCollectionCreateRequest,
        )

    def processJobsCollectionCreateRequest(
        self,
        message: dict,
    ) -> bool:

        try:
            logger.info(message)

            # Extract organization data object
            organizationDataObject = self.extractOrganizationDataObject(message)

            # Check if the jobs collection for the organization exists
            collectionExists = self.doesCollectionExist(
                organizationDataObject.organizationId,
            )

            # Create the jobs collection if it does not exist
            if not collectionExists:
                self.createCollection()

            return True

        except Exception as e:
            logger.error(f"Error processing jobs collection creation: {e}")
            return False

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
            indexKey="organizationId",
            isUnique=True,
        )
        logger.info(f"Creating collection [{collectionName}] succeeded.")
