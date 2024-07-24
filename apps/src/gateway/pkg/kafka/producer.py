import os
import logging

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class Producer:

    def __init__(
        self,
        bootstrap_servers,
        topic,
    ):
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
        )

    def produce(
        self,
        data,
    ):
        self.producer.send(self.topic, data)
        self.producer.flush()
