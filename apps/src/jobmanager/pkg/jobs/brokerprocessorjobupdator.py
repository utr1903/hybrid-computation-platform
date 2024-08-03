import json
import logging
import uuid
from datetime import datetime

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from pkg.data.jobs import JobCreateRequestDto, JobUpdateRequestDto, JobDataObject
from pkg.jobs.brokerprocessor import BrokerProcessor

logger = logging.getLogger(__name__)


class BrokerProcessorJobUpdator(BrokerProcessor):
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
            self.processJobUpdateRequest,
        )

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.cache.connect()
        self.brokerConsumer.connect()

    def processJobUpdateRequest(
        self,
        message: dict,
    ) -> None:

        try:
            logger.info(message)

            # Parse message
            messageParsed = self.parseMessage(message)

            # Extract job request DTO
            jobUpdateRequestDto = self.extractJobUpdateRequestDto(messageParsed)

            # Get job from individual job collection
            job = self.getJobFromIndividualJobCollection(jobUpdateRequestDto)

            # Create job data object
            jobDataObject = self.createJobDataObject(job, jobUpdateRequestDto)

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

    def extractJobUpdateRequestDto(
        self,
        message: dict,
    ) -> JobUpdateRequestDto:

        return JobUpdateRequestDto(
            organizationId=message.get("organizationId"),
            jobId=message.get("jobId"),
            jobName=message.get("jobName"),
            jobStatus=message.get("jobStatus"),
        )

    def getJobFromIndividualJobCollection(
        self,
        jobUpdateRequestDto: JobUpdateRequestDto,
    ) -> dict:
        logger.info(f"Getting job [{jobUpdateRequestDto.jobId}]...")
        job = self.database.findMany(
            databaseName=jobUpdateRequestDto.organizationId,
            collectionName=jobUpdateRequestDto.jobId,
            query={},
            sort=[("jobVersion", -1)],
            limit=1,
        )
        if job is None:
            msg = f"Job [{jobUpdateRequestDto.jobId}] not found."
            logger.error(msg)
            raise Exception(msg)

        logger.info(f"Getting job [{jobUpdateRequestDto.jobId}] succeeded.")
        return job[0]

    def createJobDataObject(
        self,
        job: dict,
        jobRequestDto: JobUpdateRequestDto,
    ) -> JobDataObject:
        jobName = (
            jobRequestDto.jobName
            if jobRequestDto.jobName is not None
            else job.get("jobName")
        )

        jobStatus = jobRequestDto.jobStatus
        if jobRequestDto.jobStatus != "SUBMITTED":
            jobStatus = "UPDATED"

        return JobDataObject(
            organizationId=jobRequestDto.organizationId,
            jobId=job.get("jobId"),
            jobName=jobName,
            jobVersion=job.get("jobVersion") + 1,
            jobStatus=jobStatus,
            timestampRequest=job.get("timestampRequest"),
            timestampCreate=job.get("timestampCreate"),
            timestampUpdate=datetime.now().timestamp(),
        )

    def processIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ):
        # Add job to individual job collection
        self.addJobToIndividualJobCollection(jobDataObject)

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
        self.updateJobInAllJobsCollection(
            jobDataObject,
        )

        # Get all jobs
        jobs = self.getAllJobs(jobDataObject.organizationId)

        # Set jobs in cache
        self.setAllJobsInCache(jobs)

    def updateJobInAllJobsCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        logger.info(f"Updating job [{jobDataObject.jobId}]...")
        self.database.update(
            databaseName=jobDataObject.organizationId,
            collectionName="jobs",
            filter={"jobId": jobDataObject.jobId},
            update={"$set": jobDataObject.toDict()},
        )
        logger.info(f"Updating job [{jobDataObject.jobId}] succeeded.")

    def getAllJobs(
        self,
        databaseName: str,
    ):
        logger.info(f"Getting all jobs...")
        results = self.database.findMany(
            databaseName=databaseName,
            collectionName="jobs",
            query={},
            sort=None,
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
