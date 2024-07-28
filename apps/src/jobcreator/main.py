import logging
import multiprocessing

from pkg.config.config import Config
from pkg.server.server import Server
from pkg.broker.kafka import Consumer


def setLoggingLevel(
    level,
):
    if level == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif level == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif level == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.INFO)


def consume_messages(
    bootstrap_servers: str,
    topic: str,
    consumer_group_id: str,
    redis_master_server: str,
    redis_port: int,
    redis_password: str,
):
    consumer = Consumer(
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        consumer_group_id=consumer_group_id,
        redis_master_server=redis_master_server,
        redis_port=int(redis_port),
        redis_password=redis_password,
    )
    consumer.consume()


def start_server():
    server = Server()
    server.run()


def main():

    # Parse config
    cfg = Config()
    if not cfg.validate():
        logging.error("Invalid configuration.")
        return

    # Set logging level
    setLoggingLevel(level=cfg.LOGGING_LEVEL)

    processes: list[multiprocessing.Process] = []
    processes.append(
        multiprocessing.Process(
            target=consume_messages,
            args=(
                cfg.KAFKA_BOOTSTRAP_SERVERS,
                cfg.KAFKA_TOPIC,
                cfg.KAFKA_CONSUMER_GROUP,
                cfg.REDIS_MASTER_SERVER,
                cfg.REDIS_PORT,
                cfg.REDIS_PASSWORD,
            ),
        )
    )
    processes.append(
        multiprocessing.Process(
            target=start_server,
        )
    )

    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
