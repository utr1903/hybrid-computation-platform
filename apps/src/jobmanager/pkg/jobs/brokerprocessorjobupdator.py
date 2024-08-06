import json
import logging
from datetime import datetime

from commons.logger.logger import Logger
from commons.database.database import Database
from commons.cache.cache import Cache
from commons.broker.consumer import BrokerConsumer
from commons.broker.producer import BrokerProducer
from pkg.data.jobs import JobUpdateRequestDto, JobDataObject
from pkg.jobs.brokerprocessor import BrokerProcessor


class BrokerProcessorJobUpdator(BrokerProcessor):
    def __init__(
        self,
        logger: Logger,
        database: Database,
        cache: Cache,
        brokerConsumer: BrokerConsumer,
        brokerProducer: BrokerProducer,
    ):
        self.logger = logger
        self.database = database
        self.cache = cache
        self.brokerConsumer = brokerConsumer
        self.brokerProducer = brokerProducer

    def run(
        self,
    ) -> None:
        # Establish connections
        self.establishConnections()

        # Consume messages
        self.brokerConsumer.consume(
            self.processJobUpdateRequest,
        )

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.cache.connect()
        self.brokerConsumer.connect()
        self.brokerProducer.connect()

    def processJobUpdateRequest(
        self,
        message: dict,
    ) -> None:

        try:
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

            # Publish job to broker
            self.publishJobSubmitted(jobDataObject)

            # Process all jobs collection
            self.processAllJobsCollection(jobDataObject)

        except Exception as e:
            self.logger.log(
                logging.ERROR,
                "Error processing job update request.",
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
        self.logger.log(
            logging.INFO,
            f"Getting job [{jobUpdateRequestDto.jobId}]...",
        )
        job = self.database.findMany(
            databaseName=jobUpdateRequestDto.organizationId,
            collectionName=jobUpdateRequestDto.jobId,
            query={},
            sort=[("jobVersion", -1)],
            limit=1,
        )
        if job is None:
            msg = f"Job [{jobUpdateRequestDto.jobId}] not found."
            self.logger.log(
                logging.ERROR,
                msg,
            )
            raise Exception(msg)

        self.logger.log(
            logging.INFO,
            f"Getting job [{jobUpdateRequestDto.jobId}] succeeded.",
        )
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

        # Add job to cache
        self.addJobToIndividualJobCache(jobDataObject)

    def addJobToIndividualJobCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        self.logger.log(
            logging.INFO,
            f"Inserting job [{jobDataObject.jobId}]...",
        )
        self.database.insert(
            databaseName=jobDataObject.organizationId,
            collectionName=jobDataObject.jobId,
            request=jobDataObject.toDict(),
        )
        self.logger.log(
            logging.INFO,
            f"Inserting job [{jobDataObject.jobId}] succeeded.",
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

    def publishJobSubmitted(
        self,
        jobDataObject: JobDataObject,
    ) -> None:
        if jobDataObject.jobStatus == "SUBMITTED":
            self.logger.log(
                logging.INFO,
                f"Publishing submitted job [{jobDataObject.jobId}] to [jobsubmitted] topic...",
            )
            self.brokerProducer.produce(
                "jobsubmitted",
                json.dumps(jobDataObject.toDict()).encode("ascii"),
            )
            self.logger.log(
                logging.INFO,
                f"Publishing submitted job [{jobDataObject.jobId}] to [jobsubmitted] topic succeeded.",
            )

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
        self.setAllJobsInCache(jobDataObject.organizationId, jobs)

    def updateJobInAllJobsCollection(
        self,
        jobDataObject: JobDataObject,
    ) -> None:

        self.logger.log(
            logging.INFO,
            f"Updating job [{jobDataObject.jobId}]...",
        )
        self.database.update(
            databaseName=jobDataObject.organizationId,
            collectionName="jobs",
            filter={"jobId": jobDataObject.jobId},
            update={"$set": jobDataObject.toDict()},
        )
        self.logger.log(
            logging.INFO,
            f"Updating job [{jobDataObject.jobId}] succeeded.",
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
            query={},
            sort=None,
            limit=100,
        )
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
