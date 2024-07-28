import json
import logging
import uuid
from datetime import datetime

from pkg.broker.consumer import BrokerConsumer
from pkg.cache.cache import Cache
from pkg.data.jobs import JobRequestDto, JobCreationDto

logger = logging.getLogger(__name__)


class JobCreator:
    def __init__(
        self,
        brokerConsumer: BrokerConsumer,
        cache: Cache,
    ):
        self.brokerConsumer = brokerConsumer
        self.cache = cache

    def run(
        self,
    ) -> None:

        self.brokerConsumer.consume(
            consumeFunction=self.processJobRequest,
        )

    def processJobRequest(
        self,
        message,
    ) -> None:

        try:
            # Extract job request DTO
            jobRequestDto = self.extractJobRequestDto(message)

            # Create job creation DTO
            jobCreationDto = self.createJobCreationDto(jobRequestDto)

            # Create job
            self.createJob(jobCreationDto)
        except:
            pass

    def extractJobRequestDto(
        self,
        message,
    ) -> JobRequestDto:

        return JobRequestDto(
            customerOrganizationId=message["customerOrganizationId"],
            customerUserId=message["customerUserId"],
            jobName=message["jobName"],
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
            jobStatus="CREATED",
            jobRequestTimestamp=jobRequestDto.jobRequestTimestamp,
            jobCreationTimestamp=datetime.now().timestamp(),
        )

    def createJob(
        self,
        jobCreationDto: JobCreationDto,
    ) -> None:

        try:
            logger.info("Setting job in cache...")
            self.cache.set(
                key="jobs",
                value=json.dumps(jobCreationDto.toDict()),
            )

            logger.info("Setting job in cache succeeded.")
        except Exception as e:
            logger.info(f"Setting job in cache failed: {e}")
