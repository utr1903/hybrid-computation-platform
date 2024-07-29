import logging
import json

from waitress import serve
from flask import Flask, request, Response

from pkg.database.database import Database
from pkg.cache.cache import Cache


logger = logging.getLogger(__name__)


class Server:

    def __init__(
        self,
        database: Database,
        cache: Cache,
    ):
        self.app = Flask(__name__)
        self.app.debug = True
        self.app.use_reloader = False
        self.register_endpoints()

        self.database = database
        self.cache = cache

    def register_endpoints(
        self,
    ):
        self.app.add_url_rule(
            rule="/livez", endpoint="livez", view_func=self.livez, methods=["GET"]
        )

        self.app.add_url_rule(
            rule="/jobs", endpoint="jobs", view_func=self.listJobs, methods=["GET"]
        )

    def livez(
        self,
    ):
        body = {"ping": "pong"}
        resp = Response(
            response=json.dumps(body),
            status=200,
            mimetype="application/json",
        )
        return resp

    def listJobs(
        self,
    ):
        try:
            # Get jobs from cache
            jobs = self.getJobsFromCache()

            if jobs is None:
                logger.info("No jobs are found in cache.")

                # Get jobs from database
                jobs = self.getJobsFromDatabase()

                # Set jobs in cache
                self.cache.set("jobs", jobs)

            logger.info(json.loads(jobs))

            resp = Response(
                response=jobs,
                status=200,
                mimetype="application/json",
            )
            return resp
        except Exception as e:
            logger.error(e)
            resp = Response(
                response=e,
                status=500,
                mimetype="application/json",
            )
            return resp

    def run(
        self,
    ):
        logger.info("Starting server...")
        serve(self.app, host="0.0.0.0", port=8080)

    def getJobsFromCache(
        self,
    ) -> bytes | None:
        logger.info("Getting jobs from cache...")
        return self.cache.get("jobs")

    def getJobsFromDatabase(
        self,
    ) -> str | None:
        jobs = self.database.findMany(
            databaseName="custoemrorg1",
            collectionName="jobs",
            query={},
            limit=10,
        )

        return json.dumps(jobs)
