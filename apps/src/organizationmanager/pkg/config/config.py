import os


class Config:

    def __init__(
        self,
    ) -> None:

        # Logging level
        self.LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")

        # Database parameters
        self.DATABASE_MASTER_ADDRESS = os.getenv("DATABASE_MASTER_ADDRESS")
        self.DATABASE_SLAVE_ADDRESS = os.getenv("DATABASE_SLAVE_ADDRESS")
        self.DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
        self.DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

        # Broker parameters
        self.BROKER_ADDRESS = os.getenv("BROKER_ADDRESS")
        self.BROKER_CONSUMER_GROUP = os.getenv("BROKER_CONSUMER_GROUP")

    def validate(self) -> bool:
        if not self.LOGGING_LEVEL:
            return False
        if self.LOGGING_LEVEL not in ["DEBUG", "INFO", "ERROR"]:
            return False

        # Validate database parameters
        if not self.DATABASE_MASTER_ADDRESS:
            return False
        if not self.DATABASE_SLAVE_ADDRESS:
            return False
        if not self.DATABASE_USERNAME:
            return False
        if not self.DATABASE_PASSWORD:
            return False

        # Validate broker parameters
        if not self.BROKER_ADDRESS:
            return False
        if not self.BROKER_CONSUMER_GROUP:
            return False

        return True
