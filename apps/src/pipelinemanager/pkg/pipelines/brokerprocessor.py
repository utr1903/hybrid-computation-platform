import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class BrokerProcessor(ABC):

    @abstractmethod
    def run(
        self,
        topic,
    ):
        pass