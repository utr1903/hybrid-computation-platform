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

    def insert(
        self,
        request: dict,
    ):
        # Get all jobs collection
        allJobsCollection, allJobsCollectionAlreadyExists = self.getAllJobsCollection(
            request["customerOrganizationId"],
        )

        # Update all jobs collection
        self.updateAllJobsCollection(
            allJobsCollection,
            allJobsCollectionAlreadyExists,
            request,
        )

    def getAllJobsCollection(
        self,
        databaseName: str,
    ) -> Tuple[Collection, bool]:
        try:
            db = self.master[databaseName]
            collectionAlreadyExists: bool

            # Create "jobs" collection if it doesn't exist
            if "jobs" not in db.list_collection_names():
                collectionAlreadyExists = False
                logger.info("The collection [jobs] does not exist. Creating...")

                # Create collection
                jobsCollection = db.create_collection("jobs")

                # Create unique index on job ID
                jobsCollection.create_index(
                    [
                        ("jobId", ASCENDING),
                    ],
                    unique=True,
                )
                logger.info("Creating collection [jobs] succeeded.")

            # Otherwise, return the collection
            else:
                collectionAlreadyExists = True
                jobsCollection = db["jobs"]

            return jobsCollection, collectionAlreadyExists
        except Exception as e:
            logger.error("Creating collection [jobs] failed.", e)

    def updateAllJobsCollection(
        self,
        collection: Collection,
        collectionExists: bool,
        request: dict,
    ):
        try:
            # Create the payload
            payload = {
                "customerUserId": request["customerUserId"],
                "jobId": request["jobId"],
                "jobName": request["jobName"],
                "jobStatus": request["jobStatus"],
                "jobVersion": request.get("jobVersion", 1),
                "jobRequestTimestamp": request["jobRequestTimestamp"],
                "jobCreationTimestamp": request["jobCreationTimestamp"],
            }

            # Insert the job immediately if the collection doesn't exist
            if not collectionExists:
                logger.info("Inserting job...")
                collection.insert_one(payload)
                logger.info("Inserting job succeeded.")
                return

            # Get the job ID
            jobId = payload["jobId"]

            # Otherwise, check if the job already exists
            job = collection.find_one(
                {"jobId": jobId},
            )

            # If the job doesn't exist, insert it
            if not job:
                logger.info("Job does not exist. Inserting...")
                collection.insert_one(payload)
                logger.info("Inserting job succeeded.")
                return

            # Otherwise, update the job with the incremented job version
            else:
                jobVersion = job["jobVersion"]
                logger.info(
                    f"Job already exists with version [{jobVersion}]. Updating..."
                )
                job["jobVersion"] = jobVersion + 1

                collection.update_one(
                    {"jobId": jobId},
                    {"$set": job},
                    upsert=True,
                )
                logger.info("Updating job succeeded.")

        except Exception as e:
            logger.error("Inserting job succeeded.", e)

    def getIndividualJobCollection(
        self,
        databaseName: str,
        collectionName: str,
    ) -> Tuple[Collection, bool]:
        try:
            db = self.master[databaseName]

            # Create individual "job" collection if it doesn't exist
            if collectionName not in db.list_collection_names():
                collectionAlreadyExists = False

                # Create collection
                jobCollection = db.create_collection(collectionName)

                # Create index
                jobCollection.create_index([("jobId", ASCENDING)], unique=True)

            # Otherwise, return the collection
            else:
                collectionAlreadyExists = True
                jobCollection = db[collectionName]

            return jobCollection, collectionAlreadyExists
        except Exception as e:
            logger.error(e)
