from abc import ABC, abstractmethod


class BrokerProducer(ABC):

    @abstractmethod
    def connect(
        self,
    ):
        pass

    @abstractmethod
    def produce(
        self,
        topic,
        data,
    ):
        pass
