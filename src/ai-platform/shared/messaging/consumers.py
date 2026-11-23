from typing import Callable

from pydantic import ValidationError

from shared.logging.logger import get_logger
from shared.messaging.rabbitmq_client import RabbitMQClient

log = get_logger(__name__)

Handler = Callable[[bytes, object], None]


class BaseConsumer:
    """Ack on success. Poison messages go to the dead-letter queue immediately;
    other failures are retried once (redelivered flag) and then dead-lettered."""

    def __init__(self, client: RabbitMQClient, queue: str, routing_keys: list[str],
                 handler: Handler, prefetch: int = 1):
        self.client = client
        self.queue = queue
        self.routing_keys = routing_keys
        self.handler = handler
        self.prefetch = prefetch

    def _on_message(self, ch, method, properties, body: bytes) -> None:
        try:
            self.handler(body, properties)
            ch.basic_ack(method.delivery_tag)
        except (ValidationError, ValueError) as exc:
            log.error("Poison message, dead-lettering: %s", exc)
            ch.basic_nack(method.delivery_tag, requeue=False)
        except Exception:  # noqa: BLE001 - transient failure path
            log.exception("Handler failed (redelivered=%s)", method.redelivered)
            ch.basic_nack(method.delivery_tag, requeue=not method.redelivered)

    def start(self) -> None:
        self.client.connect()
        self.client.declare_queue(self.queue, self.routing_keys)
        ch = self.client.channel
        ch.basic_qos(prefetch_count=self.prefetch)
        ch.basic_consume(self.queue, on_message_callback=self._on_message)
        log.info("Consuming from %s", self.queue)
        try:
            ch.start_consuming()
        except KeyboardInterrupt:
            ch.stop_consuming()
        finally:
            self.client.close()
