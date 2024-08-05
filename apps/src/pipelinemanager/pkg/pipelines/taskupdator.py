import json
import logging

from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.tasks import (
    TaskDataObject,
    TaskUpdateRequestDto,
)
from pkg.pipelines.brokerprocessor import BrokerProcessor

logger = logging.getLogger(__name__)


class BrokerProcessorTaskUpdator(BrokerProcessor):
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

            # Extract task update request DTO
            taskUpdateRequestDto = self.extractTaskUpdateRequestDto(messageParsed)

            # Get task from tasks collection
            task = self.getTaskFromTasksCollection(taskUpdateRequestDto)

            # Update task data object
            taskDataObject = self.createTaskDataObject(task, taskUpdateRequestDto)

            # Add task to tasks collection
            self.updateTaskInTasksCollection(taskDataObject)

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

        if "timestampUpdated" not in messageParsed:
            missingFields.append("timestampUpdated")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message validation succeeded.")

    def extractTaskUpdateRequestDto(
        self,
        message: dict,
    ) -> TaskUpdateRequestDto:

        return TaskUpdateRequestDto(
            organizationId=message.get("organizationId"),
            taskId=message.get("taskId"),
            taskStatus=message.get("taskStatus"),
            timestampUpdated=message.get("timestampUpdate"),
        )

    def getTaskFromTasksCollection(
        self,
        taskUpdateRequestDto: TaskUpdateRequestDto,
    ) -> dict:
        logger.info(f"Getting task [{taskUpdateRequestDto.taskId}]...")
        task = self.database.findOne(
            databaseName="pipelines",
            collectionName="tasks",
            query={"taskId": taskUpdateRequestDto.taskId},
        )
        if task is None:
            msg = f"Task [{taskUpdateRequestDto.taskId}] not found."
            logger.error(msg)
            raise Exception(msg)

        logger.info(f"Getting task [{taskUpdateRequestDto.taskId}] succeeded.")
        return task

    def createTaskDataObject(
        self,
        task: dict,
        taskUpdateRequestDto: TaskUpdateRequestDto,
    ) -> TaskDataObject:
        return TaskDataObject(
            organizationId=taskUpdateRequestDto.organizationId,
            jobId=task.get("jobId"),
            jobVersion=task.get("jobVersion"),
            timestampCreated=task.get("timestampCreated"),
            taskId=taskUpdateRequestDto.taskId,
            taskStatus=taskUpdateRequestDto.taskStatus,
        )

    def updateTaskInTasksCollection(
        self,
        taskDataObject: TaskDataObject,
    ) -> None:

        logger.info(f"Updating task [{taskDataObject.taskId}]...")
        self.database.update(
            databaseName="pipelines",
            collectionName="tasks",
            filter={"taskId": taskDataObject.taskId},
            update={"$set": taskDataObject.toDict()},
        )
        logger.info(f"Updating task [{taskDataObject.taskId}] succeeded.")
