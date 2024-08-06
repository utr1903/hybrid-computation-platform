import json
import logging
import uuid

from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.tasks import (
    TaskDataObject,
    TaskCreateRequestDto,
)
from pkg.tasks.brokerprocessor import BrokerProcessor

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
        # Establish connections
        self.establishConnections()

        # Consume messages
        self.brokerConsumer.consume(
            self.processTaskCreateRequest,
        )

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

            # Parse message
            messageParsed = self.parseMessage(message)

            # Extract task create request DTO
            taskCreateRequestDto = self.extractTaskCreateRequestDto(messageParsed)

            # Create task data object
            taskDataObject = self.createTaskDataObject(taskCreateRequestDto)

            # Add task to tasks collection
            self.addTaskToTasksCollection(taskDataObject)

        except Exception as e:
            logger.error(e)

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

        if "jobId" not in messageParsed:
            missingFields.append("jobId")

        if "jobVersion" not in messageParsed:
            missingFields.append("jobVersion")
        
        if "timestampUpdate" not in messageParsed:
            missingFields.append("timestampUpdate")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message validation succeeded.")

    def extractTaskCreateRequestDto(
        self,
        message: dict,
    ) -> TaskCreateRequestDto:

        return TaskCreateRequestDto(
            organizationId=message.get("organizationId"),
            jobId=message.get("jobId"),
            jobVersion=message.get("jobVersion"),
            timestampCreated=message.get("timestampUpdate"),
        )

    def createTaskDataObject(
        self,
        taskCreateRequestDto: TaskCreateRequestDto,
    ) -> TaskDataObject:
        return TaskDataObject(
            organizationId=taskCreateRequestDto.organizationId,
            jobId=taskCreateRequestDto.jobId,
            jobVersion=taskCreateRequestDto.jobVersion,
            timestampCreated=taskCreateRequestDto.timestampCreated,
            taskId=str(uuid.uuid4()),
            taskStatus="CREATED",
        )

    def addTaskToTasksCollection(
        self,
        taskDataObject: TaskDataObject,
    ) -> None:

        logger.info(f"Inserting task [{taskDataObject.taskId}]...")
        self.database.insert(
            databaseName="tasks",
            collectionName="tasks",
            request=taskDataObject.toDict(),
        )
        logger.info(f"Inserting task [{taskDataObject.taskId}] succeeded.")
