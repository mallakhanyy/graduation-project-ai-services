import pika
from pydantic import BaseModel

from shared.messaging.rabbitmq_client import RabbitMQClient


class JsonPublisher:
    """Publishes pydantic contracts as persistent camelCase JSON messages."""

    def __init__(self, client: RabbitMQClient):
        self.client = client

    def publish(self, routing_key: str, message: BaseModel, correlation_id: str | None = None) -> None:
        self.client.channel.basic_publish(
            exchange=self.client.exchange,
            routing_key=routing_key,
            body=message.model_dump_json(by_alias=True).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                correlation_id=correlation_id,
            ),
        )
