import logging
from typing import Tuple
from datetime import datetime
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class Database(ABC):

    @abstractmethod
    def connect(
        self,
    ) -> None:
        pass

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
        sort: list[Tuple[str, int]],
        limit: int,
    ) -> list[dict] | None:
        pass
