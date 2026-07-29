import asyncio
import json
import aio_pika

from shared.config import settings


async def main():
    connection = await aio_pika.connect_robust(
        host=settings.rabbitmq.host,
        port=settings.rabbitmq.port,
        login=settings.rabbitmq.user,
        password=settings.rabbitmq.password,
        virtualhost=settings.rabbitmq.vhost,
    )

    channel = await connection.channel()

    queue = await channel.declare_queue(
        settings.rabbitmq.results_queue,
        durable=True,
    )

    print("Waiting for transcription result...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():

                result = json.loads(message.body.decode("utf-8"))

                print(f"Correlation ID : {message.correlation_id}")
                print(f"Request ID     : {result['request_id']}")
                print(f"Status         : {result['status']}")
                print(f"Text           : {result['text']}")
                print(f"Processing Time: {result['processing_time']:.2f} sec")
                print(f"Error          : {result['error']}")

                break

    await connection.close()


asyncio.run(main())