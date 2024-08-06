import logging

from commons.database.database import Database


logger = logging.getLogger(__name__)


class TasksCollectionCreator:
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

            # Check if the tasks collection exists
            collectionExists = self.doesCollectionExist()

            # Create the tasks collection if it does not exist
            if not collectionExists:
                self.createCollection()

            return True

        except Exception as e:
            logger.error(f"Error processing tasks create request: {e}")
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

        logger.info(f"Collection [{collectionName}] does not exist. Creating...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="taskId",
            isUnique=True,
        )
        logger.info(f"Creating collection [{collectionName}] succeeded.")
