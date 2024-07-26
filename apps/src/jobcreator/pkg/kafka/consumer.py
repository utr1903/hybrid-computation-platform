import json
import logging

from kafka import KafkaConsumer
from pkg.redis.client import RedisClient

logger = logging.getLogger(__name__)


class Consumer:

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        consumer_group_id: str,
        redis_master_server: str,
        redis_port: int,
        redis_password: str,
    ):
        # Kafka
        self.topic = topic
        self.consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            group_id=consumer_group_id,
            value_deserializer=lambda m: json.loads(m.decode("ascii")),
        )

        # Redis
        self.cache = RedisClient(
            redis_master_server=redis_master_server,
            redis_port=redis_port,
            redis_password=redis_password,
        )

    def consume(
        self,
    ):
        logger.info("Starting consumer...")
        self.consumer.subscribe([self.topic])
        for message in self.consumer:
            logger.info(message.value)
            self.cache.set(
                key="job",
                value=json.dumps(message.value),
            )
            logger.info("Message is set in Redis.")
