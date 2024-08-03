import logging
import json

from waitress import serve
from flask import Flask, request, Response

from pkg.broker.producer import BrokerProducer

logger = logging.getLogger(__name__)


class Server:

    def __init__(
        self,
        producer: BrokerProducer,
    ):
        self.app = Flask(__name__)
        self.app.debug = False
        self.app.use_reloader = False
        self.register_endpoints()

        self.producer = producer

    def register_endpoints(
        self,
    ):
        self.app.add_url_rule(
            rule="/livez", endpoint="livez", view_func=self.livez, methods=["GET"]
        )
        self.app.add_url_rule(
            rule="/upload", endpoint="upload", view_func=self.upload, methods=["POST"]
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

    def upload(self):
        data = request.get_data()
        logger.debug(data)

        if not data:
            return Response(
                response=json.dumps({"result": "Failed."}),
                status=400,
                mimetype="application/json",
            )

        # Publish to broker
        self.producer.produce(data)

        return Response(
            response=json.dumps({"result": "Suceeded."}),
            status=202,
            mimetype="application/json",
        )

    def run(
        self,
    ):
        serve(self.app, host="0.0.0.0", port=8080)
