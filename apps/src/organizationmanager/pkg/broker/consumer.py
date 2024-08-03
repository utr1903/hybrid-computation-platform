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
        if "organizationName" not in messageParsed:
            missingFields.append("organizationName")

        if len(missingFields) > 0:
            msg = f"There are missing fields which have to be defined: {missingFields}"
            logger.error(msg)
            raise Exception(msg)

        logger.info("Message validation succeeded.")
