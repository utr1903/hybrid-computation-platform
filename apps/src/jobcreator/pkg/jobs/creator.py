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
        message,
    ) -> None:

        try:
            logger.info(message)

            # Extract job request DTO
            jobRequestDto = self.extractJobRequestDto(message)

            # Create job creation DTO
            jobCreationDto = self.createJobCreationDto(jobRequestDto)

            # Create job
            self.createJob(jobCreationDto)
        except Exception as e:
            logger.error(e)

    def extractJobRequestDto(
        self,
        message,
    ) -> JobRequestDto:

        return JobRequestDto(
            customerOrganizationId=message["customerOrganizationId"],
            customerUserId=message["customerUserId"],
            jobName=message["jobName"],
            jobVersion=message["jobVersion"],
            jobRequestTimestamp=message["jobRequestTimestamp"],
        )

    def createJobCreationDto(
        self,
        jobRequestDto: JobRequestDto,
    ) -> JobCreationDto:
        return JobCreationDto(
            customerOrganizationId=jobRequestDto.customerOrganizationId,
            customerUserId=jobRequestDto.customerUserId,
            jobId=str(uuid.uuid4()),
            jobName=jobRequestDto.jobName,
            jobVersion=jobRequestDto.jobVersion,
            jobStatus="CREATED",
            jobRequestTimestamp=jobRequestDto.jobRequestTimestamp,
            jobCreationTimestamp=datetime.now().timestamp(),
        )

    def createJob(
        self,
        jobCreationDto: JobCreationDto,
    ) -> None:

        try:
            logger.info("Inserting job in database...")
            self.database.insert(
                request=jobCreationDto.toDict(),
            )
            logger.info("Inserting job in database succeeded.")
        except Exception as e:
            logger.info(f"Inserting job in database failed: {e}")
            return

        try:
            logger.info("Setting job in cache...")
            self.cache.set(
                key="jobs",
                value=json.dumps(jobCreationDto.toDict()),
            )

            logger.info("Setting job in cache succeeded.")
        except Exception as e:
            logger.info(f"Setting job in cache failed: {e}")
