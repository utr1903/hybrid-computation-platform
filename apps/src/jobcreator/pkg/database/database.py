import logging
import uuid
from datetime import datetime
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class Database(ABC):

    @abstractmethod
    def insert(
        self,
        request: dict,
    ):
        pass
