import json
import logging
import uuid
import multiprocessing
from datetime import datetime

from pkg.database.database import Database
from pkg.cache.cache import Cache
from pkg.broker.consumer import BrokerConsumer
from pkg.data.jobs import JobRequestDto, JobCreationDto
from pkg.jobs.jobcreator import JobCreator
from pkg.jobs.jobscollectioncreator import JobsCollectionCreator

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(
        self,
        database: Database,
        cache: Cache,
    ):
        self.database = database
        self.cache = cache
        self.brokerConsumer = brokerConsumer

    def run(
        self,
    ) -> None:

        processes: list[multiprocessing.Process] = []
        processes.append(
            multiprocessing.Process(
                target=self.processJobsCollectionCreateRequest,
            )
        )
        processes.append(
            multiprocessing.Process(
                target=self.processJobCreateRequest,
            )
        )
        for p in processes:
            p.start()

        for p in processes:
            p.join()

    def processJobsCollectionCreateRequest(
        self,
    ) -> None:
        JobsCollectionCreator(
            self.database,
            self.cache,
            self.brokerConsumer,
        ).run("organizationcreated")

    def processJobCreateRequest(
        self,
    ) -> None:
        JobCreator(
            self.database,
            self.cache,
            self.brokerConsumer,
        ).run("createjob")
