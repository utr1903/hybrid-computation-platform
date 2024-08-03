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
