import logging
import uuid

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from apps.src.pipelinemanager.pkg.data.tasks import (
    TaskDataObject,
    TaskCreateRequestDto,
)
from pkg.pipelines.brokerprocessor import BrokerProcessor

logger = logging.getLogger(__name__)


class BrokerProcessorTaskCreator(BrokerProcessor):
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
        self.establishConnections()

        self.brokerConsumer.consume(self.processTaskCreateRequest)

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.cache.connect()
        self.brokerConsumer.connect()

    def processTaskCreateRequest(
        self,
        message: dict,
    ) -> None:

        try:
            logger.info(message)

            # Extract task create request DTO
            taskCreateRequestDto = self.extractTaskCreateRequestDto(message)

            # Create task data object
            taskDataObject = self.createTaskDataObject(taskCreateRequestDto)

            # Add task to pipelines collection
            self.addTaskToPipelinesCollection(taskDataObject)

        except Exception as e:
            logger.error(e)

    def extractTaskCreateRequestDto(
        self,
        message: dict,
    ) -> TaskCreateRequestDto:

        return TaskCreateRequestDto(
            organizationId=message.get("organizationId"),
            jobId=message.get("jobId"),
            jobVersion=message.get("jobVersion"),
            timestampSubmitted=message.get("timestampSubmitted"),
        )

    def createTaskDataObject(
        self,
        taskCreateRequestDto: TaskCreateRequestDto,
    ) -> TaskDataObject:
        return TaskDataObject(
            organizationId=taskCreateRequestDto.organizationId,
            jobId=taskCreateRequestDto.jobId,
            jobVersion=taskCreateRequestDto.jobVersion,
            timestampSubmitted=taskCreateRequestDto.timestampSubmitted,
            taskId=str(uuid.uuid4()),
            taskStatus="CREATED",
        )

    def addTaskToPipelinesCollection(
        self,
        taskDataObject: TaskDataObject,
    ) -> None:

        logger.info(f"Inserting task [{taskDataObject.taskId}]...")
        self.database.insert(
            databaseName="pipelines",
            collectionName="pipelines",
            request=taskDataObject.toDict(),
        )
        logger.info(f"Inserting task [{taskDataObject.taskId}] succeeded.")
