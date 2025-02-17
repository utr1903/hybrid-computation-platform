import logging
import json

from waitress import serve
from flask import Flask, request, Response

from commons.logger.logger import Logger
from commons.broker.producer import BrokerProducer


class Server:

    def __init__(
        self,
        logger: Logger,
        producer: BrokerProducer,
    ):
        self.logger = logger

        self.app = Flask(__name__)
        self.app.debug = False
        self.app.use_reloader = False
        self.register_endpoints()

        self.producer = producer
        self.PRODUCER_TOPIC_CREATE = "createorganization"

    def register_endpoints(
        self,
    ):
        self.app.add_url_rule(
            rule="/livez", endpoint="livez", view_func=self.livez, methods=["GET"]
        )
        self.app.add_url_rule(
            rule="/create", endpoint="create", view_func=self.create, methods=["POST"]
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

    def create(self):
        data = request.get_data()

        if not data:
            return Response(
                response=json.dumps({"result": "Failed."}),
                status=400,
                mimetype="application/json",
            )

        # Publish to broker
        self.producer.produce(
            self.PRODUCER_TOPIC_CREATE,
            data,
        )

        return Response(
            response=json.dumps({"result": "Suceeded."}),
            status=202,
            mimetype="application/json",
        )

    def run(
        self,
    ):
        # Establish connections
        self.establishConnections()

        # Start server
        self.logger.log(
            logging.INFO,
            "Starting server...",
        )
        serve(self.app, host="0.0.0.0", port=8080)

    def establishConnections(
        self,
    ) -> None:
        self.producer.connect()
