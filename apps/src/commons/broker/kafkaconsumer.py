from kafka import KafkaConsumer

from commons.broker.consumer import BrokerConsumer


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
        self.consumer.subscribe([self.topic])

        for message in self.consumer:
            # Consume message with given external function
            consumeFunction(message.value)
