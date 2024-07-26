import logging
import json

from waitress import serve
from flask import Flask, request, Response

from pkg.redis.client import RedisClient


logger = logging.getLogger(__name__)


class Server:

    def __init__(
        self,
        cache: RedisClient,
    ):
        self.app = Flask(__name__)
        self.app.debug = False
        self.app.use_reloader = False
        self.register_endpoints()

        self.cache = cache

    def register_endpoints(
        self,
    ):
        self.app.add_url_rule(
            rule="/livez", endpoint="livez", view_func=self.livez, methods=["GET"]
        )

        self.app.add_url_rule(
            rule="/jobs", endpoint="jobs", view_func=self.list_jobs, methods=["GET"]
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

    def list_jobs(
        self,
    ):
        try:
            jobs = json.loads(self.cache.get("jobs"))
            logger.info(jobs)

            resp = Response(
                response=json.dumps(jobs),
                status=200,
                mimetype="application/json",
            )
            return resp
        except Exception as e:
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
