import logging
import json

from waitress import serve
from flask import Flask, Response


logger = logging.getLogger(__name__)


class Server:

    def __init__(
        self,
    ):
        self.app = Flask(__name__)
        self.app.debug = False
        self.app.use_reloader = False
        self.register_endpoints()

    def register_endpoints(
        self,
    ):
        self.app.add_url_rule(
            rule="/livez", endpoint="livez", view_func=self.livez, methods=["GET"]
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

    def run(
        self,
    ):
        logger.info("Starting server...")
        serve(self.app, host="0.0.0.0", port=8080)
