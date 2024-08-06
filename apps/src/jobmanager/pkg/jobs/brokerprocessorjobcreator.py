import json
import logging
import uuid
from datetime import datetime

from commons.logger.logger import Logger
from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from pkg.data.jobs import JobCreateRequestDto, JobDataObject
from pkg.jobs.brokerprocessor import BrokerProcessor


class BrokerProcessorJobCreator(BrokerProcessor):
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
            self.processJobCreateRequest,
        )

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.cache.connect()
        self.brokerConsumer.connect()

    def processJobCreateRequest(
        self,
        message: dict,
    ) -> None:

        try:
            self.logger.log(
                logging.INFO,
                message,
            )

            # Parse message
            messageParsed = self.parseMessage(message)

            # Extract job request DTO
            jobCreateRequestDto = self.extractJobCreateRequestDto(messageParsed)

            # Create job data object
            jobDataObject = self.createJobDataObject(jobCreateRequestDto)

            # Process individual job collection
            self.processIndividualJobCollection(jobDataObject)

            # Process all jobs collection
            self.processAllJobsCollection(jobDataObject)

        except Exception as e:
            self.logger.log(
                logging.ERROR,
                "Error processing job create request.",
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

        if "jobName" not in messageParsed:
            missingFields.append("jobName")

        if len(missingFields) > 0:
            msg = "There are missing fields which have to be defined."
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

    def extractJobCreateRequestDto(
        self,
        message: dict,
    ) -> JobCreateRequestDto:

        return JobCreateRequestDto(
            organizationId=message.get("organizationId"),
            jobName=message.get("jobName"),
            timestampRequest=message.get("timestampRequest"),
        )

    def createJobDataObject(
        self,
        jobRequestDto: JobCreateRequestDto,
    ) -> JobDataObject:
        return JobDataObject(
            organizationId=jobRequestDto.organizationId,
            jobId=str(uuid.uuid4()),
            jobName=jobRequestDto.jobName,
            jobVersion=1,
            jobStatus="CREATED",
            timestampRequest=jobRequestDto.timestampRequest,
            timestampCreate=datetime.now().timestamp(),
            timestampUpdate=None,
        )

    def processIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ):
        # Create individual job collection
        self.createIndividualJobCollection(jobDataObject)

        # Add job to individual job collection
        self.addJobToIndividualJobCollection(jobDataObject)

        # Add job to cache
        self.addJobToIndividualJobCache(jobDataObject)

    def createIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ):
        databaseName = jobDataObject.organizationId
        collectionName = jobDataObject.jobId

        self.logger.log(
            logging.INFO,
            f"Creating collection [{collectionName}] in database...",
        )
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="jobVersion",
            isUnique=True,
        )
        self.logger.log(
            logging.INFO,
            f"Creating collection [{collectionName}] in database succeeded.",
        )

    def addJobToIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        self.logger.log(
            logging.INFO,
            f"Inserting job [{jobDataObject.jobId}] into database...",
        )
        self.database.insert(
            databaseName=jobDataObject.organizationId,
            collectionName=jobDataObject.jobId,
            request=jobDataObject.toDict(),
        )
        self.logger.log(
            logging.INFO,
            f"Inserting job [{jobDataObject.jobId}] into database succeeded.",
        )

    def addJobToIndividualJobCache(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        self.logger.log(
            logging.INFO,
            f"Setting job [{jobDataObject.jobId}] in cache...",
        )
        self.cache.set(
            key=f"{jobDataObject.organizationId}-{jobDataObject.jobId}",
            value=json.dumps(jobDataObject.toDict()),
        )
        self.logger.log(
            logging.INFO,
            f"Setting job [{jobDataObject.jobId}] in cache succeeded.",
        )

    def processAllJobsCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        # Check to all jobs collection
        self.addJobToAllJobsCollection(
            jobDataObject,
        )

        # Get all jobs
        jobs = self.getAllJobs(jobDataObject.organizationId)

        # Set jobs in cache
        self.setAllJobsInCache(jobDataObject.organizationId, jobs)

    def addJobToAllJobsCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        self.logger.log(
            logging.INFO,
            f"Inserting job [{jobDataObject.jobId}] to all jobs collection...",
        )
        self.database.insert(
            databaseName=jobDataObject.organizationId,
            collectionName="jobs",
            request=jobDataObject.toDict(),
        )
        self.logger.log(
            logging.INFO,
            f"Inserting job [{jobDataObject.jobId}] to all jobs collection succeeded.",
        )

    def getAllJobs(
        self,
        databaseName: str,
    ):
        self.logger.log(
            logging.INFO,
            f"Getting all jobs...",
        )
        results = self.database.findMany(
            databaseName=databaseName,
            collectionName="jobs",
            sort=None,
            query={},
            limit=100,
        )

        if results is None:
            self.logger.log(
                logging.ERROR,
                f"Getting all jobs failed.",
            )
            return []

        self.logger.log(
            logging.INFO,
            f"Getting all jobs succeeded.",
        )

        jobs: list[dict] = []
        result: dict
        for result in results:
            jobs.append(
                {
                    "jobId": result.get("jobId"),
                    "jobName": result.get("jobName"),
                    "jobStatus": result.get("jobStatus"),
                    "jobVersion": result.get("jobVersion"),
                }
            )
        return jobs

    def setAllJobsInCache(
        self,
        organizationId: str,
        jobs: list[dict],
    ):
        self.logger.log(
            logging.INFO,
            f"Setting jobs in cache.",
        )
        self.cache.set(
            key=f"{organizationId}-jobs",
            value=json.dumps(jobs),
        )
        self.logger.log(
            logging.INFO,
            f"Setting jobs in cache succeeded.",
        )
