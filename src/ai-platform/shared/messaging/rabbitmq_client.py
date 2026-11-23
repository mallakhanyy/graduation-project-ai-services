import time

import pika

from shared.logging.logger import get_logger

log = get_logger(__name__)


class RabbitMQClient:
    """Thin blocking-connection wrapper: connect with retry, declare topology."""

    def __init__(self, url: str, exchange: str, retries: int = 10, delay_s: float = 3.0):
        self.url = url
        self.exchange = exchange
        self.retries = retries
        self.delay_s = delay_s
        self._connection: pika.BlockingConnection | None = None
        self._channel = None

    def connect(self) -> None:
        for attempt in range(1, self.retries + 1):
            try:
                self._connection = pika.BlockingConnection(pika.URLParameters(self.url))
                self._channel = self._connection.channel()
                self._channel.exchange_declare(self.exchange, "topic", durable=True)
                self._channel.exchange_declare(f"{self.exchange}.dlx", "fanout", durable=True)
                log.info("Connected to RabbitMQ")
                return
            except pika.exceptions.AMQPConnectionError:
                log.warning("RabbitMQ not ready (attempt %d/%d)", attempt, self.retries)
                time.sleep(self.delay_s)
        raise ConnectionError("Could not connect to RabbitMQ")

    @property
    def channel(self):
        if self._channel is None or self._channel.is_closed:
            self.connect()
        return self._channel

    def declare_queue(self, queue: str, routing_keys: list[str]) -> None:
        ch = self.channel
        ch.queue_declare(f"{queue}.dead", durable=True)
        ch.queue_bind(f"{queue}.dead", f"{self.exchange}.dlx")
        ch.queue_declare(
            queue,
            durable=True,
            arguments={"x-dead-letter-exchange": f"{self.exchange}.dlx"},
        )
        for key in routing_keys:
            ch.queue_bind(queue, self.exchange, routing_key=key)

    def close(self) -> None:
        if self._connection and self._connection.is_open:
            self._connection.close()
