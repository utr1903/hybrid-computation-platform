import json
import logging

from commons.logger.logger import Logger
from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.tasks import (
    TaskDataObject,
    TaskUpdateRequestDto,
)
from pkg.tasks.brokerprocessor import BrokerProcessor


class BrokerProcessorTaskUpdator(BrokerProcessor):
    def __init__(
        self,
        logger: Logger,
        database: Database,
        cache: Cache,
        brokerConsumer: BrokerConsumer,
    ):
        self.logger = logger
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
            self.logger.log(
                logging.ERROR,
                "Error processing task update request.",
                attrs={"error": str(e)},
            )

    def parseMessage(
        self,
        message,
    ) -> dict:

        self.logger.log("Parsing message...")

        try:
            messageParsed = json.loads(message)
        except Exception as e:
            self.logger.log(
                logging.ERROR,
                "Message parsing failed.",
                attrs={"error": str(e)},
            )
            raise Exception("Message parsing failed: {e}")

        self.validateMessage(messageParsed)

        return messageParsed

    def validateMessage(
        self,
        messageParsed,
    ) -> None:

        self.logger.log(
            logging.INFO,
            "Validating message...",
        )

        missingFields = []
        if "organizationId" not in messageParsed:
            missingFields.append("organizationId")

        if "timestampUpdated" not in messageParsed:
            missingFields.append("timestampUpdated")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            self.logger.log(
                logging.ERROR,
                msg,
                attrs={
                    "missingFields": ",".join(map(str, missingFields)),
                },
            )
            raise Exception(msg)

        self.logger.log(
            logging.INFO,
            "Message validation succeeded.",
        )

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
        self.logger.log(
            logging.INFO,
            f"Getting task [{taskUpdateRequestDto.taskId}]...",
        )
        task = self.database.findOne(
            databaseName="tasks",
            collectionName="tasks",
            query={"taskId": taskUpdateRequestDto.taskId},
        )
        if task is None:
            msg = f"Task [{taskUpdateRequestDto.taskId}] not found."
            self.logger.log(
                logging.ERROR,
                msg,
            )
            raise Exception(msg)

        self.logger.log(
            logging.INFO,
            f"Getting task [{taskUpdateRequestDto.taskId}] succeeded.",
        )
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

        self.logger.log(
            logging.INFO,
            f"Updating task [{taskDataObject.taskId}]...",
        )
        self.database.update(
            databaseName="tasks",
            collectionName="tasks",
            filter={"taskId": taskDataObject.taskId},
            update={"$set": taskDataObject.toDict()},
        )
        self.logger.log(
            logging.INFO,
            f"Updating task [{taskDataObject.taskId}] succeeded.",
        )
