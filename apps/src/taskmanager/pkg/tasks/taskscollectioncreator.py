import logging

from commons.logger.logger import Logger
from commons.database.database import Database


class TasksCollectionCreator:
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

            # Check if the tasks collection exists
            collectionExists = self.doesCollectionExist()

            # Create the tasks collection if it does not exist
            if not collectionExists:
                self.createCollection()

            return True

        except Exception as e:
            self.logger.log(
                logging.ERROR,
                f"Error processing tasks create request: {e}",
                attrs={"error": str(e)},
            )
            return False

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()

    def doesCollectionExist(
        self,
    ):
        return self.database.doesCollectionExist(
            databaseName="tasks",
            collectionName="tasks",
        )

    def createCollection(
        self,
    ):
        databaseName = "tasks"
        collectionName = "tasks"

        self.logger.log(
            logging.INFO,
            f"Collection [{collectionName}] does not exist. Creating...",
        )
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="taskId",
            isUnique=True,
        )
        self.logger.log(
            logging.INFO,
            f"Creating collection [{collectionName}] succeeded.",
        )
