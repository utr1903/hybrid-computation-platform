import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class BrokerConsumer(ABC):

    @abstractmethod
    def connect(
        self,
    ):
        pass

    @abstractmethod
    def consume(
        self,
        consumeFunction,
    ):
        pass
