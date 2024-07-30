import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class BrokerConsumer(ABC):

    @abstractmethod
    def consume(
        self,
        consumeFunction,
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

        if "jobVersion" not in messageParsed:
            missingFields.append("jobVersion")

        if "jobRequestTimestamp" not in messageParsed:
            missingFields.append("jobRequestTimestamp")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message validation succeeded.")
