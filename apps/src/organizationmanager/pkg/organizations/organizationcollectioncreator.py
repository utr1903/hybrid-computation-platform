import logging

from commons.logger.logger import Logger
from commons.database.database import Database


class OrganizationCollectionCreator:
    def __init__(
        self,
        logger: Logger,
        database: Database,
    ):
        self.logger = logger
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
            self.logger.log(
                logging.ERROR,
                "Error processing organization create request.",
                attrs={"error": str(e)},
            )
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

        self.logger.log(
            logging.INFO,
            f"Collection [{collectionName}] does not exist. Creating...",
        )
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="organizationId",
            isUnique=True,
        )
        self.logger.log(
            logging.INFO,
            f"Creating collection [{collectionName}] succeeded.",
        )
