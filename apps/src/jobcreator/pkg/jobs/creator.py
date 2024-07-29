import json
import logging
import uuid
from datetime import datetime

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from pkg.data.jobs import JobRequestDto, JobCreationDto

logger = logging.getLogger(__name__)


class JobCreator:
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

        self.brokerConsumer.consume(self.processJobRequest)

    def processJobRequest(
        self,
        message: dict,
    ) -> None:

        try:
            logger.info(message)

            # Extract job request DTO
            jobRequestDto = self.extractJobRequestDto(message)

            # Create job creation DTO
            jobCreationDto = self.createJobCreationDto(jobRequestDto)

            # Check if jobs collection exists
            if not self.doesAllJobsCollectionExist(jobCreationDto):

                # Create jobs collection
                self.createAllJobsCollection(jobCreationDto)

                # Add job to all jobs collection
                job = self.addJobToAllJobsCollection(jobCreationDto)

                # Set jobs in cache
                self.setAllJobsInCache([job])

            # If jobs collection exist, check if the individual job already exists
            else:

                # Get the job from all jobs collection if it exists
                job = self.getJobInAllJobsCollection(jobCreationDto)

                # If job doesn't exist, add it
                if job is None:
                    job = self.addJobToAllJobsCollection(
                        jobCreationDto,
                    )
                # Otherwise, update the job and increment the version
                else:
                    self.updateJobInAllJobsCollection(
                        jobCreationDto,
                    )

                # Get all jobs
                jobs = self.getAllJobs(jobCreationDto.customerOrganizationId)

                # Set jobs in cache
                self.setAllJobsInCache(jobs)

        except Exception as e:
            logger.error(e)

    def extractJobRequestDto(
        self,
        message: dict,
    ) -> JobRequestDto:

        return JobRequestDto(
            customerOrganizationId=message.get("customerOrganizationId"),
            customerUserId=message.get("customerUserId"),
            jobName=message.get("jobName"),
            jobId=message.get(
                "jobId", str(uuid.uuid4())
            ),  # Generate new if not provided
            jobVersion=message.get("jobVersion"),
            jobRequestTimestamp=message.get("jobRequestTimestamp"),
        )

    def createJobCreationDto(
        self,
        jobRequestDto: JobRequestDto,
    ) -> JobCreationDto:
        return JobCreationDto(
            customerOrganizationId=jobRequestDto.customerOrganizationId,
            customerUserId=jobRequestDto.customerUserId,
            jobId=jobRequestDto.jobId,
            jobName=jobRequestDto.jobName,
            jobVersion=jobRequestDto.jobVersion,
            jobStatus="CREATED",
            jobRequestTimestamp=jobRequestDto.jobRequestTimestamp,
            jobCreationTimestamp=datetime.now().timestamp(),
        )

    def doesAllJobsCollectionExist(
        self,
        jobCreationDto: JobCreationDto,
    ):
        return self.database.doesCollectionExist(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName="jobs",
        )

    def createAllJobsCollection(
        self,
        jobCreationDto: JobCreationDto,
    ):
        databaseName = jobCreationDto.customerOrganizationId
        collectionName = "jobs"

        logger.info(f"Collection [{databaseName}] does not exist. Creating...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="jobId",
            isUnique=True,
        )
        logger.info(f"Creating collection [{databaseName}] succeeded.")

    def addJobToAllJobsCollection(
        self,
        jobCreationDto: JobCreationDto,
    ) -> dict:

        logger.info(f"Inserting job [{jobCreationDto.jobId}]...")
        job = self.database.insert(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName="jobs",
            request=jobCreationDto.toDict(),
        )
        logger.info(f"Inserting job [{jobCreationDto.jobId}] succeeded.")

        return job

    def getJobInAllJobsCollection(
        self,
        jobCreationDto: JobCreationDto,
    ) -> dict | None:

        logger.info(f"Getting job [{jobCreationDto.jobId}]...")
        job = self.database.findOne(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName="jobs",
            query={"jobId": jobCreationDto.jobId},
        )

        if job is None:
            logger.info(f"Job [{jobCreationDto.jobId}] does not exist.")
        else:
            logger.info(f"Getting [{jobCreationDto.jobId}] succeeded.")

    def updateJobInAllJobsCollection(
        self,
        job: dict,
    ):
        jobId = job.get("jobId")
        logger.info(f"Updating job [{jobId}]...")
        job["jobVersion"] += 1

        self.database.update(
            filter={"jobId": jobId},
            update={"$set": job},
        )
        logger.info(f"Updating job [{jobId}] succeeded.")

    def getAllJobs(
        self,
        customerOrganizationId: str,
    ):
        logger.info(f"Getting all jobs...")
        jobs = self.database.findMany(
            databaseName=customerOrganizationId,
            collectionName="jobs",
            query={},
            limit=100,
        )
        logger.info(f"Getting all jobs succeeded.")

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
