import json
import logging
import uuid
from datetime import datetime

from kafka import KafkaConsumer
from pkg.cache.cache import Cache
from pkg.data.jobs import JobRequestDto, JobCreationDto

logger = logging.getLogger(__name__)


class BrokerConsumerKafka:

    def __init__(
        self,
        bootstrapServers: str,
        topic: str,
        consumerGroupId: str,
        cache: Cache,
    ):
        # Kafka
        self.topic = topic
        self.consumer = KafkaConsumer(
            bootstrap_servers=bootstrapServers,
            group_id=consumerGroupId,
            # value_deserializer=lambda m: json.loads(m.decode("ascii")),
        )

        # Redis
        self.cache = cache

    def consume(
        self,
    ):
        logger.info("Starting consumer...")
        self.consumer.subscribe([self.topic])
        for message in self.consumer:

            try:
                logger.info(message.value)

                jobRequestDto = self.parseMessage(message=message)

                jobCreationDto = self.createJobCreationDto(jobRequestDto=jobRequestDto)

                self.createJob(jobCreationDto=jobCreationDto)
            except:
                pass

    def parseMessage(
        self,
        message,
    ) -> JobRequestDto:

        logger.info("Parsing message...")

        try:
            messageParsed = json.loads(message.value)
        except Exception as e:
            logger.error(e)
            raise Exception("Message parsing failed: {e}")

        missingFields = []
        if "customerOrganizationId" not in messageParsed:
            missingFields.append("customerOrganizationId")

        if "customerUserId" not in messageParsed:
            missingFields.append("customerUserId")

        if "jobName" not in messageParsed:
            missingFields.append("jobName")

        if "jobRequestTimestamp" not in messageParsed:
            missingFields.append("jobRequestTimestamp")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message parsing succeeded.")
        return JobRequestDto(
            customerOrganizationId=messageParsed["customerOrganizationId"],
            customerUserId=messageParsed["customerUserId"],
            jobName=messageParsed["jobName"],
            jobRequestTimestamp=messageParsed["jobRequestTimestamp"],
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
