import os


class Config:

    def __init__(self) -> None:

        # Logging level
        self.LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")

        # Broker parameters
        self.BROKER_ADDRESS = os.getenv("BROKER_ADDRESS")
        self.BROKER_TOPIC = os.getenv("BROKER_TOPIC")

    def validate(self) -> bool:
        if not self.LOGGING_LEVEL:
            return False
        if self.LOGGING_LEVEL not in ["DEBUG", "INFO", "ERROR"]:
            return False
        if not self.BROKER_ADDRESS:
            return False
        if not self.BROKER_TOPIC:
            return False
        return True
