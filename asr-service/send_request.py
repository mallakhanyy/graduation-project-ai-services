import asyncio
import uuid
import aio_pika

from shared.config import settings

AUDIO_FILE = "tests/9_256_cropped.flac"
EXTENSION = ".flac"


async def main():
    connection = await aio_pika.connect_robust(
        host=settings.rabbitmq.host,
        port=settings.rabbitmq.port,
        login=settings.rabbitmq.user,
        password=settings.rabbitmq.password,
        virtualhost=settings.rabbitmq.vhost,
    )

    channel = await connection.channel()

    with open(AUDIO_FILE, "rb") as f:
        audio = f.read()

    request_id = str(uuid.uuid4())

    message = aio_pika.Message(
        body=audio,
        correlation_id=request_id,
        headers={"extension": EXTENSION},
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    await channel.default_exchange.publish(
        message,
        routing_key=settings.rabbitmq.requests_queue,
    )

    print(f"Sent request: {request_id}")

    await connection.close()


asyncio.run(main())