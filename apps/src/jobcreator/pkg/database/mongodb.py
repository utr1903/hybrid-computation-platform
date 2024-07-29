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
        masterAddress: str,
        slaveAddress: str,
        username: str,
        password: str,
    ):

        self.master = MongoClient(
            "mongodb://%s:%s@%s"
            % (quote_plus(username), quote_plus(password), masterAddress)
        )
        # self.master.admin.command('ping')

        self.slave = MongoClient(
            "mongodb://%s:%s@%s"
            % (quote_plus(username), quote_plus(password), slaveAddress)
        )

    def doesCollectionExist(
        self,
        databaseName: str,
        collectionName: str,
    ) -> bool:
        db = self.slave[databaseName]
        return collectionName in db.list_collection_names()

    def createCollection(
        self,
        databaseName: str,
        collectionName: str,
    ) -> None:
        db = self.master[databaseName]
        db.create_collection(collectionName)

    def createIndexOnCollection(
        self,
        databaseName: str,
        collectionName: str,
        indexKey: str,
        isUnique: bool,
    ) -> None:
        collection = self.master[databaseName][collectionName]
        collection.create_index(
            [
                (indexKey),
            ],
            unique=isUnique,
        )

    def insert(
        self,
        databaseName: str,
        collectionName: str,
        request: dict,
    ) -> None:
        self.master[databaseName][collectionName].insert_one(request)

    def update(
        self,
        databaseName: str,
        collectionName: str,
        filter: dict,
        update: dict,
    ) -> None:
        self.master[databaseName][collectionName].update_one(
            filter,
            update,
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
        limit: int,
    ) -> dict | None:
        return self.slave[databaseName][collectionName].find(
            query,
            limit=limit,
        )
