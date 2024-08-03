import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class BrokerProducer(ABC):

    @abstractmethod
    def produce(
        self,
        topic,
        data,
    ):
        pass
