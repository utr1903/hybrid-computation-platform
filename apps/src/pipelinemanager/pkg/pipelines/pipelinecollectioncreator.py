import logging

from pkg.database.database import Database


logger = logging.getLogger(__name__)


class PipelineCollectionCreator:
    def __init__(
        self,
        database: Database,
    ):
        self.database = database

    def run(
        self,
    ) -> bool:

        try:

            # Check if the pipelines collection exists
            collectionExists = self.doesPipelinesCollectionExist()

            # Create the pipelines collection if it does not exist
            if not collectionExists:
                self.createCollection()

            return True

        except Exception as e:
            logger.error(f"Error processing pipeline create request: {e}")
            return False

    def doesPipelinesCollectionExist(
        self,
    ):
        return self.database.doesCollectionExist(
            databaseName="pipelines",
            collectionName="pipelines",
        )

    def createCollection(
        self,
    ):
        databaseName = "pipelines"
        collectionName = "pipelines"

        logger.info(f"Collection [{collectionName}] does not exist. Creating...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="taskId",
            isUnique=True,
        )
        logger.info(f"Creating collection [{collectionName}] succeeded.")
