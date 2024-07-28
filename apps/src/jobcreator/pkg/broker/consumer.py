import logging
import uuid
from datetime import datetime
from abc import ABC, abstractmethod

from pkg.data.jobs import JobRequestDto, JobCreationDto

logger = logging.getLogger(__name__)


class BrokerConsumer(ABC):

    @abstractmethod
    def consume(
        self,
    ):
        pass

    def validateMessage(
        self,
        messageParsed,
    ) -> None:

        logger.info("Validating message...")

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

        logger.info("Message validation succeeded.")
