import os


class Config:

    def __init__(self) -> None:

        # Logging level
        self.LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")

        # Redis parameters
        self.REDIS_MASTER_SERVER = os.getenv("REDIS_MASTER_SERVER")
        self.REDIS_SLAVE_SERVERS = os.getenv("REDIS_SLAVE_SERVERS")
        self.REDIS_PORT = os.getenv("REDIS_PORT")
        self.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    def validate(self) -> bool:
        if not self.LOGGING_LEVEL:
            return False
        if self.LOGGING_LEVEL not in ["DEBUG", "INFO", "ERROR"]:
            return False
        if not self.REDIS_MASTER_SERVER:
            return False
        if not self.REDIS_SLAVE_SERVERS:
            return False
        if not self.REDIS_PORT:
            return False
        if not self.REDIS_PASSWORD:
            return False
        return True
