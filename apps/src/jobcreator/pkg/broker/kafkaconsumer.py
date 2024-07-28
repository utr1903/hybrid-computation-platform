import logging
import json
from kafka import KafkaConsumer

from pkg.broker.consumer import BrokerConsumer
from pkg.cache.cache import Cache
from pkg.data.jobs import JobRequestDto, JobCreationDto

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
            # value_deserializer=lambda m: json.loads(m.decode("ascii")),
        )

    def consume(
        self,
        consumeFunction,
    ):
        logger.info("Starting consumer...")
        self.consumer.subscribe([self.topic])

        for message in self.consumer:
            try:
                # Parse message
                messageParsed = self.parseMessage(message=message)

                # Consume message with given external function
                consumeFunction(messageParsed)
            except:
                pass

    def parseMessage(
        self,
        message,
    ) -> dict:

        logger.info("Parsing message...")

        try:
            messageParsed = json.loads(message.value)
        except Exception as e:
            logger.error(e)
            raise Exception("Message parsing failed: {e}")

        self.validateMessage(messageParsed)

        return messageParsed
