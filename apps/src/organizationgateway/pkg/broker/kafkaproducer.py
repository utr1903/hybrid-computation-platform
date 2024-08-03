import logging
from kafka import KafkaProducer

from pkg.broker.producer import BrokerProducer

logger = logging.getLogger(__name__)


class BrokerProducerKafka(BrokerProducer):

    def __init__(
        self,
        bootstrap_servers,
    ):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
        )

    def produce(
        self,
        topic,
        data,
    ):
        self.producer.send(topic, data)
        self.producer.flush()
