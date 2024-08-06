import json
import logging
import uuid

from commons.logger.logger import Logger
from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.tasks import (
    TaskDataObject,
    TaskCreateRequestDto,
)
from pkg.tasks.brokerprocessor import BrokerProcessor


class BrokerProcessorTaskCreator(BrokerProcessor):
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

            # Extract task create request DTO
            taskCreateRequestDto = self.extractTaskCreateRequestDto(messageParsed)

            # Create task data object
            taskDataObject = self.createTaskDataObject(taskCreateRequestDto)

            # Add task to tasks collection
            self.addTaskToTasksCollection(taskDataObject)

        except Exception as e:
            self.logger.log(
                logging.ERROR,
                "Error processing task create request.",
                attrs={"error": str(e)},
            )

    def parseMessage(
        self,
        message,
    ) -> dict:

        self.logger.log(
            logging.INFO,
            "Parsing message...",
        )

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

        if "jobId" not in messageParsed:
            missingFields.append("jobId")

        if "jobVersion" not in messageParsed:
            missingFields.append("jobVersion")

        if "timestampUpdate" not in messageParsed:
            missingFields.append("timestampUpdate")

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

        self.logger.log(
            logging.INFO,
            f"Inserting task [{taskDataObject.taskId}]...",
        )
        self.database.insert(
            databaseName="tasks",
            collectionName="tasks",
            request=taskDataObject.toDict(),
        )
        self.logger.log(
            logging.INFO,
            f"Inserting task [{taskDataObject.taskId}] succeeded.",
        )
