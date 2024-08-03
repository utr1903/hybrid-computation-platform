import logging
from kafka import KafkaConsumer

from pkg.broker.consumer import BrokerConsumer

logger = logging.getLogger(__name__)


class BrokerConsumerKafka(BrokerConsumer):

    def __init__(
        self,
        bootstrapServers: str,
        topic: str,
        consumerGroupId: str,
    ):
        self.topic = topic
        self.bootstrapServers = bootstrapServers
        self.consumerGroupId = consumerGroupId

    def connect(
        self,
    ):
        self.consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrapServers,
            group_id=self.consumerGroupId,
        )

    def consume(
        self,
        consumeFunction,
    ):
        logger.info("Starting consumer...")
        self.consumer.subscribe([self.topic])

        for message in self.consumer:
            try:
                # Consume message with given external function
                consumeFunction(message.value)
            except Exception as e:
                logger.error(e)
