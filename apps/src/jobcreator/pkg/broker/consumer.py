from abc import ABC, abstractmethod


class BrokerConsumer(ABC):

    @abstractmethod
    def consume(
        self,
    ):
        pass
