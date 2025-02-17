from abc import ABC, abstractmethod


class Database(ABC):

    @abstractmethod
    def connect(
        self,
    ) -> None:
        pass

    @abstractmethod
    def doesCollectionExist(
        self,
        databaseName: str,
        collectionName: str,
    ) -> bool:
        pass

    @abstractmethod
    def createCollection(
        self,
        databaseName: str,
        collectionName: str,
    ):
        pass

    @abstractmethod
    def createIndexOnCollection(
        self,
        databaseName: str,
        collectionName: str,
        indexKey: str,
        isUnique: bool,
    ):
        pass

    @abstractmethod
    def insert(
        self,
        databaseName: str,
        collectionName: str,
        request: dict,
    ) -> None:
        pass

    @abstractmethod
    def update(
        self,
        databaseName: str,
        collectionName: str,
        filter: dict,
        update: dict,
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
        limit: int,
    ) -> list[dict] | None:
        pass
