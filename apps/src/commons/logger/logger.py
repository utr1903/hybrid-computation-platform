import logging
from pythonjsonlogger import jsonlogger


class Logger:
    def __init__(
        self,
        level: str,
    ) -> None:

        # Get logger
        self.logger = logging.getLogger()

        # Set logging level
        if level == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
        elif level == "INFO":
            self.logger.setLevel(logging.INFO)
        elif level == "ERROR":
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.setLevel(logging.INFO)

        # Set JSON logging format
        logHandler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        logHandler.setFormatter(formatter)
        self.logger.addHandler(logHandler)

    def log(
        self,
        level: int,
        message: str,
        attrs: dict = {},
    ) -> None:
        attrs["level"] = logging.getLevelName(level)
        self.logger.log(
            level,
            message,
            extra=attrs,
        )
