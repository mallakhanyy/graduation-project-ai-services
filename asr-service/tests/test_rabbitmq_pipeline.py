import asyncio
import json
import uuid
from pathlib import Path

import aio_pika

from shared.config import settings


AUDIO_FILE = "tests/9_166_cropped.flac"


async def main():

    connection = await aio_pika.connect_robust(
        host=settings.rabbitmq.host,
        port=settings.rabbitmq.port,
        login=settings.rabbitmq.user,
        password=settings.rabbitmq.password,
        virtualhost=settings.rabbitmq.vhost,
    )

    channel = await connection.channel()

    requests_queue = await channel.declare_queue(
        settings.rabbitmq.requests_queue,
        durable=True,
    )

    results_queue = await channel.declare_queue(
        settings.rabbitmq.results_queue,
        durable=True,
    )

    request_id = str(uuid.uuid4())

    audio_path = Path(AUDIO_FILE)

    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    print(f"Sending request: {request_id}")

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=audio_path.read_bytes(),
            correlation_id=request_id,
            content_type="audio/wav",
            headers={
                "extension": audio_path.suffix.lstrip(".")
            },
        ),
        routing_key=requests_queue.name,
    )

    print("Waiting for transcription...\n")

    async with results_queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                if message.correlation_id != request_id:
                    continue

                result = json.loads(message.body.decode())

                print("=" * 60)
                print("Transcription Result")
                print("=" * 60)
                print(json.dumps(result, indent=4, ensure_ascii=False))
                print("=" * 60)

                break

    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())