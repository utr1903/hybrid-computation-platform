import logging
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class Database(ABC):

    @abstractmethod
    def findOne(
        self,
        databaseName: str,
        collectionName: str,
        query: dict,
    ) -> dict | None:
        pass

    @abstractmethod
    def findMany(
        self,
        databaseName: str,
        collectionName: str,
        query: dict,
        limit: int,
    ) -> list[dict] | None:
        pass
