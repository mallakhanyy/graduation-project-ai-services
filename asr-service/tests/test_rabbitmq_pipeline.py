import asyncio
import json
import uuid
from datetime import timedelta

import aio_pika
from minio import Minio

from shared.config import settings


AUDIO_FILE = "audio2878.wav"
MINIO_BUCKET = "asr-audio"
MINIO_HOST = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"


async def main():

    # -----------------------------
    # 1. Generate a fresh presigned URL
    # -----------------------------
    minio_client = Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    audio_url = minio_client.presigned_get_object(
        MINIO_BUCKET,
        AUDIO_FILE,
        expires=timedelta(minutes=15),
    )

    # -----------------------------
    # 2. Connect to RabbitMQ
    # -----------------------------
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

    # -----------------------------
    # 3. Build request payload
    # -----------------------------
    request = {
        "audio_url": audio_url,
        "extension": AUDIO_FILE.rsplit(".", 1)[-1],
    }

    print(f"Sending request: {request_id}")
    print(f"Audio file: {AUDIO_FILE}")

    # -----------------------------
    # 4. Publish JSON request
    # -----------------------------
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(request).encode("utf-8"),
            correlation_id=request_id,
            content_type="application/json",
        ),
        routing_key=requests_queue.name,
    )

    print("Waiting for transcription...\n")

    # -----------------------------
    # 5. Wait for matching result
    # -----------------------------
    async with results_queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                if message.correlation_id != request_id:
                    continue

                result = json.loads(
                    message.body.decode("utf-8")
                )

                print("=" * 60)
                print("Transcription Result")
                print("=" * 60)
                print(
                    json.dumps(
                        result,
                        indent=4,
                        ensure_ascii=False,
                    )
                )
                print("=" * 60)

                break

    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())