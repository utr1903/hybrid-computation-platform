import json
import logging
import uuid
from datetime import datetime

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from pkg.data.jobs import JobCreateRequestDto, JobDataObject
from pkg.jobs.brokerprocessor import BrokerProcessor

logger = logging.getLogger(__name__)


class BrokerProcessorJobCreator(BrokerProcessor):
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
            logger.info(message)

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

        if "jobName" not in messageParsed:
            missingFields.append("jobName")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message validation succeeded.")

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

    def createIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ):
        databaseName = jobDataObject.organizationId
        collectionName = jobDataObject.jobId

        logger.info(f"Creating collection [{collectionName}]...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="jobVersion",
            isUnique=True,
        )
        logger.info(f"Creating collection [{collectionName}] succeeded.")

    def addJobToIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        logger.info(f"Inserting job [{jobDataObject.jobId}]...")
        self.database.insert(
            databaseName=jobDataObject.organizationId,
            collectionName=jobDataObject.jobId,
            request=jobDataObject.toDict(),
        )
        logger.info(f"Inserting job [{jobDataObject.jobId}] succeeded.")

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
        self.setAllJobsInCache(jobs)

    def addJobToAllJobsCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        logger.info(f"Inserting job [{jobDataObject.jobId}]...")
        self.database.insert(
            databaseName=jobDataObject.organizationId,
            collectionName="jobs",
            request=jobDataObject.toDict(),
        )
        logger.info(f"Inserting job [{jobDataObject.jobId}] succeeded.")

    def getAllJobs(
        self,
        databaseName: str,
    ):
        logger.info(f"Getting all jobs...")
        results = self.database.findMany(
            databaseName=databaseName,
            collectionName="jobs",
            sort=None,
            query={},
            limit=100,
        )
        logger.info(f"Getting all jobs succeeded.")

        jobs: list[dict] = []
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
        jobs: list[dict],
    ):
        logger.info(f"Setting jobs in cache.")
        self.cache.set(
            key="jobs",
            value=json.dumps(jobs),
        )
        logger.info(f"Setting jobs in cache succeeded.")
