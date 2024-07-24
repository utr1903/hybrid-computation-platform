import os


class Config:

    def __init__(self) -> None:

        # Logging level
        self.LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")

        # Kafka parameters
        self.KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        self.KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

    def validate(self) -> bool:
        if not self.LOGGING_LEVEL:
            return False
        if self.LOGGING_LEVEL not in ["DEBUG", "INFO", "ERROR"]:
            return False
        if not self.KAFKA_BOOTSTRAP_SERVERS:
            return False
        if not self.KAFKA_TOPIC:
            return False
        return True
