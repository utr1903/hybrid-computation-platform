import logging
import multiprocessing

from pkg.jobs.brokerprocessor import BrokerProcessor


logger = logging.getLogger(__name__)


class JobManager:
    def __init__(
        self,
        brokerProcessors: list[BrokerProcessor],
    ):
        self.brokerProcessors = brokerProcessors

    def run(
        self,
    ) -> None:

        processes: list[multiprocessing.Process] = []
        for brokerProcessor in self.brokerProcessors:
            processes.append(
                multiprocessing.Process(
                    target=brokerProcessor.run,
                )
            )

        for p in processes:
            p.start()

        for p in processes:
            p.join()
