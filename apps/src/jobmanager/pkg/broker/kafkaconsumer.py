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
        # Kafka
        self.topic = topic
        self.consumer = KafkaConsumer(
            bootstrap_servers=bootstrapServers,
            group_id=consumerGroupId,
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
