import json
import logging
import uuid
from datetime import datetime

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from pkg.data.jobs import JobRequestDto, JobCreationDto

logger = logging.getLogger(__name__)


class BrokerProcessorJobCreator:
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

        self.brokerConsumer.consume(self.processJobCreateRequest)

    def processJobCreateRequest(
        self,
        message: dict,
    ) -> None:

        try:
            logger.info(message)

            # Extract job request DTO
            jobRequestDto = self.extractJobRequestDto(message)

            # Create job creation DTO
            jobCreationDto = self.createJobCreationDto(jobRequestDto)

            # Process all jobs collection
            self.processAllJobsCollection(jobCreationDto)

            # Process individual job collection
            self.processIndividualJobCollection(jobCreationDto)

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

    def processAllJobsCollection(
        self,
        jobCreationDto: JobCreationDto,
    ) -> None:

        # Check if jobs collection exists
        if not self.doesAllJobsCollectionExist(jobCreationDto):

            # Create jobs collection
            self.createAllJobsCollection(jobCreationDto)

            # Add job to all jobs collection
            self.addJobToAllJobsCollection(jobCreationDto)

            # Get the job from all jobs collection if it exists
            job = self.getJobInAllJobsCollection(jobCreationDto)

            # Set jobs in cache
            self.setAllJobsInCache([job])

        # If jobs collection exist, check if the individual job already exists
        else:

            # Get the job from all jobs collection if it exists
            job = self.getJobInAllJobsCollection(jobCreationDto)

            # If job doesn't exist, add it
            if job is None:
                self.addJobToAllJobsCollection(
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

        logger.info(f"Collection [jobs] does not exist. Creating...")
        self.database.createCollection(databaseName, collectionName)
        self.database.createIndexOnCollection(
            databaseName=databaseName,
            collectionName=collectionName,
            indexKey="jobId",
            isUnique=True,
        )
        logger.info(f"Creating collection [jobs] succeeded.")

    def addJobToAllJobsCollection(
        self,
        jobCreationDto: JobCreationDto,
    ) -> None:

        logger.info(f"Inserting job [{jobCreationDto.jobId}]...")
        self.database.insert(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName="jobs",
            request=jobCreationDto.toDict(),
        )
        logger.info(f"Inserting job [{jobCreationDto.jobId}] succeeded.")

    def getJobInAllJobsCollection(
        self,
        jobCreationDto: JobCreationDto,
    ) -> dict | None:

        logger.info(f"Getting job [{jobCreationDto.jobId}]...")
        result = self.database.findOne(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName="jobs",
            query={"jobId": jobCreationDto.jobId},
        )

        if result is None:
            logger.info(f"Job [{jobCreationDto.jobId}] does not exist.")
            return None
        else:
            logger.info(f"Getting [{jobCreationDto.jobId}] succeeded.")
            return {
                "customerUserId": result.get("customerUserId"),
                "jobId": result.get("jobId"),
                "jobName": result.get("jobName"),
                "jobStatus": result.get("jobStatus"),
                "jobVersion": result.get("jobVersion"),
                "jobRequestTimestamp": result.get("jobRequestTimestamp"),
                "jobCreationTimestamp": result.get("jobCreationTimestamp"),
            }

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
        results = self.database.findMany(
            databaseName=customerOrganizationId,
            collectionName="jobs",
            query={},
            limit=100,
        )
        logger.info(f"Getting all jobs succeeded.")

        jobs: list[dict] = []
        for result in results:
            jobs.append(
                {
                    "customerUserId": result.get("customerUserId"),
                    "jobId": result.get("jobId"),
                    "jobName": result.get("jobName"),
                    "jobStatus": result.get("jobStatus"),
                    "jobVersion": result.get("jobVersion"),
                    "jobRequestTimestamp": result.get("jobRequestTimestamp"),
                    "jobCreationTimestamp": result.get("jobCreationTimestamp"),
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

    def processIndividualJobCollection(
        self,
        jobCreationDto: JobCreationDto,
    ):
        # Check if individual job collection exists
        if not self.doesIndividualJobCollectionExist(jobCreationDto):

            # Create individual job collection
            self.createIndividualJobCollection(jobCreationDto)

            # Add job to individual job collection
            self.addJobToIndividualJobCollection(jobCreationDto)

    def doesIndividualJobCollectionExist(
        self,
        jobCreationDto: JobCreationDto,
    ):
        return self.database.doesCollectionExist(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName=jobCreationDto.jobId,
        )

    def createIndividualJobCollection(
        self,
        jobCreationDto: JobCreationDto,
    ):
        databaseName = jobCreationDto.customerOrganizationId
        collectionName = jobCreationDto.jobId

        logger.info(f"Collection [{collectionName}] does not exist. Creating...")
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
        jobCreationDto: JobCreationDto,
    ) -> None:

        logger.info(
            f"Inserting job [{jobCreationDto.jobId}] with version [{jobCreationDto.jobVersion}]..."
        )
        self.database.insert(
            databaseName=jobCreationDto.customerOrganizationId,
            collectionName=jobCreationDto.jobId,
            request=jobCreationDto.toDict(),
        )
        logger.info(
            f"Inserting job [{jobCreationDto.jobId}] with version [{jobCreationDto.jobVersion}] succeeded."
        )
