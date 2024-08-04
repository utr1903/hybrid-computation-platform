import logging

from typing import Tuple
from urllib.parse import quote_plus
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection

from pkg.database.database import Database

logger = logging.getLogger(__name__)


class DatabaseMongoDb(Database):
    def __init__(
        self,
        slaveAddress: str,
        username: str,
        password: str,
    ):
        self.slaveAddress = slaveAddress
        self.username = username
        self.password = password

    def connect(
        self,
    ) -> None:
        self.slave = MongoClient(
            "mongodb://%s:%s@%s"
            % (quote_plus(self.username), quote_plus(self.password), self.slaveAddress)
        )

    def findOne(
        self,
        databaseName: str,
        collectionName: str,
        query: dict,
    ) -> dict | None:
        return self.slave[databaseName][collectionName].find_one(
            query,
        )

    def findMany(
        self,
        databaseName: str,
        collectionName: str,
        query: dict,
        sort: list[Tuple[str, int]],
        limit: int,
    ) -> list[dict] | None:
        cursor = self.slave[databaseName][collectionName].find(
            query,
            sort=sort,
            limit=limit,
        )

        items = []
        for item in cursor:
            items.append(item)

        return items
