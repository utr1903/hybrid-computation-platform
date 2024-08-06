import logging
import json

from waitress import serve
from flask import Flask, Response, request

from commons.database.database import Database
from commons.cache.cache import Cache


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
            rule="/livez",
            endpoint="livez",
            view_func=self.livez,
            methods=["GET"],
        )

        self.app.add_url_rule(
            rule="/list",
            endpoint="list",
            view_func=self.listJobs,
            methods=["GET"],
        )

        self.app.add_url_rule(
            rule="/get/<string:jobId>",
            endpoint="get",
            view_func=self.getJob,
            methods=["GET"],
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
            # Get organization ID from query params
            organizationId = request.args.get("organizationId")
            if organizationId is None:
                return Response(
                    response="Organization is not provided.",
                    status=401,
                    mimetype="application/json",
                )

            # Get jobs from cache
            jobs = self.getJobsFromCache(organizationId)

            if jobs is None:
                logger.info("No jobs are found in cache.")

                # Get jobs from database
                jobs = self.getJobsFromDatabase()

                # Set jobs in cache
                self.cache.set(f"{organizationId}-jobs", jobs)

            logger.info(json.loads(jobs))

            resp = Response(
                response=jobs,
                status=200,
                mimetype="application/json",
            )
            return resp
        except Exception as e:
            logger.error(e)
            return Response(
                response=e,
                status=500,
                mimetype="application/json",
            )

    def getJob(
        self,
        jobId: str,
    ):
        try:
            # Get organization ID from query params
            organizationId = request.args.get("organizationId")
            if organizationId is None:
                return Response(
                    response="Organization is not provided.",
                    status=401,
                    mimetype="application/json",
                )

            # Get job from cache
            job = self.getJobFromCache(jobId)

            if job is None:
                logger.info(f"Job [{jobId}] not found in cache.")

                # Get job from database
                job = self.getJobFromDatabase(jobId)

                # Set job in cache
                self.cache.set(jobId, job)

            logger.info(json.loads(job))

            resp = Response(
                response=job,
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
        # Establish connections
        self.establishConnections()

        # Start server
        logger.info("Starting server...")
        serve(self.app, host="0.0.0.0", port=8080)

    def establishConnections(
        self,
    ) -> None:
        self.database.connect()
        self.cache.connect()

    def getJobsFromCache(
        self,
        organizationId: str,
    ) -> bytes | None:
        logger.info("Getting jobs from cache...")
        return self.cache.get(f"{organizationId}-jobs")

    def getJobsFromDatabase(
        self,
        organizationId: str,
    ) -> str | None:
        logger.info("Getting jobs from database...")
        jobs = self.database.findMany(
            databaseName=organizationId,
            collectionName="jobs",
            query={},
            limit=10,
        )

        return json.dumps(jobs)

    def getJobFromCache(
        self,
        organizationId: str,
        jobId: str,
    ) -> bytes | None:
        logger.info(f"Getting job [{jobId}] from cache...")
        return self.cache.get(f"{organizationId}-{jobId}")

    def getJobFromDatabase(
        self,
        organizationId: str,
        jobId: str,
    ) -> str | None:
        result = self.database.findOne(
            databaseName=organizationId,
            collectionName=jobId,
            query={
                "jobId": jobId,
            },
        )

        return json.dumps(
            {
                "jobId": result.get("jobId"),
                "jobName": result.get("jobName"),
                "jobStatus": result.get("jobStatus"),
                "jobVersion": result.get("jobVersion"),
                "timestampRequest": result.get("timestampRequest"),
                "timestampCreate": result.get("timestampCreate"),
                "timestampUpdate": result.get("timestampUpdate"),
            }
        )
