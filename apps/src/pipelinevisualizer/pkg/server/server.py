import logging
import json

from waitress import serve
from flask import Flask, Response

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
            rule="/livez", endpoint="livez", view_func=self.livez, methods=["GET"]
        )

        self.app.add_url_rule(
            rule="/task-to-run",
            endpoint="task-ro-run",
            view_func=self.getTaskToRun,
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

    def getTaskToRun(
        self,
    ):
        try:
            # Get task to run from database
            task = self.getTaskToRunFromDatabase()
            if task is None:
                return Response(
                    response={},
                    status=200,
                    mimetype="application/json",
                )

            logger.info(json.loads(task))

            return Response(
                response=task,
                status=200,
                mimetype="application/json",
            )

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

    def getTaskToRunFromDatabase(
        self,
    ) -> str | None:
        tasks = self.database.findMany(
            databaseName="pipelines",
            collectionName="tasks",
            query={"taskStatus": "CREATED"},
            sort=[("timestampCreated", 1)],
            limit=1,
        )
        if not tasks:
            return None

        task: dict = tasks[0]
        return json.dumps(
            {
                "organizationId": task.get("organizationId"),
                "jobId": task.get("jobId"),
                "jobVersion": task.get("jobVersion"),
                "taskId": task.get("taskId"),
            }
        )
