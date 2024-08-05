import logging

from commons.database.database import Database


logger = logging.getLogger(__name__)


class OrganizationCollectionCreator:
    def __init__(
        self,
        database: Database,
    ):
        self.database = database

    def run(
        self,
    ) -> bool:

        try:
            # Establish connections
            self.establishConnections()

            # Check if the organizations collection exists
            collectionExists = self.doesOrganizationsCollectionExist()

            # Create the organizations collection if it does not exist
            if not collectionExists:
                self.createCollection()

            return True

        except Exception as e:
            logger.error(f"Error processing organization create request: {e}")
            return False

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()

    def doesOrganizationsCollectionExist(
        self,
    ):
        return self.database.doesCollectionExist(
            databaseName="organizations",
            collectionName="organizations",
        )

    def createCollection(
        self,
    ):
        databaseName = "organizations"
        collectionName = "organizations"

        logger.info(f"Collection [{collectionName}] does not exist. Creating...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="organizationId",
            isUnique=True,
        )
        logger.info(f"Creating collection [{collectionName}] succeeded.")
