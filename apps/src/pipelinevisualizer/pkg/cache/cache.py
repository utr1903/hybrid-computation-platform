from abc import ABC, abstractmethod


class Cache(ABC):

    @abstractmethod
    def connect(
        self,
    ) -> None:
        pass

    @abstractmethod
    def set(
        self,
        key,
        value,
    ) -> None:
        pass
