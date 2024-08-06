from abc import ABC, abstractmethod


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
