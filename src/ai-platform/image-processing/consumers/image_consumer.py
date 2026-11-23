from minio import Minio
from pydantic import ValidationError

from services.vision_service import VisionService, build_vision_service
from shared.configuration.settings import Settings, get_settings
from shared.contracts.query_contract import ModalityType, QuerySubmittedMessage
from shared.contracts.vision_contract import VisionRequest, VisionResult, VisionStatus
from shared.logging.logger import get_logger
from shared.messaging.consumers import BaseConsumer
from shared.messaging.publishers import JsonPublisher
from shared.messaging.rabbitmq_client import RabbitMQClient

log = get_logger(__name__)


class MinioFetcher:
    def __init__(self, settings: Settings):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

    def fetch(self, bucket: str, key: str) -> bytes:
        response = self.client.get_object(bucket, key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()


class ImageConsumer:
    """query.submitted -> VisionService -> vision.completed.

    A result is ALWAYS published (even FAILED) so the fusion stage never waits
    forever on a missing modality.
    """

    def __init__(self, settings: Settings, service: VisionService,
                 fetcher: MinioFetcher, publisher: JsonPublisher):
        self.settings = settings
        self.service = service
        self.fetcher = fetcher
        self.publisher = publisher

    def handle(self, body: bytes, properties: object) -> None:
        message = QuerySubmittedMessage.model_validate_json(body)  # ValidationError -> DLQ
        if ModalityType.IMAGE not in message.modalities or not message.image_keys:
            log.info("Query %s has no image modality; ignoring", message.query_id)
            return

        request = VisionRequest(
            query_id=message.query_id,
            bucket=message.bucket,
            image_keys=message.image_keys[: self.settings.max_images_per_query],
            language=message.language,
        )
        try:
            images = [(k, self.fetcher.fetch(request.bucket, k)) for k in request.image_keys]
            result = self.service.analyze(request, images)
        except Exception as exc:  # noqa: BLE001
            log.exception("Vision processing failed for %s", message.query_id)
            result = VisionResult(query_id=message.query_id, status=VisionStatus.FAILED, error=str(exc))

        self.publisher.publish(
            self.settings.vision_completed_routing_key, result, correlation_id=message.query_id
        )
        log.info("Query %s -> %s (%s ms)", message.query_id, result.status.value, result.processing_ms)


def main() -> None:
    settings = get_settings()
    client = RabbitMQClient(settings.rabbitmq_url, settings.events_exchange)
    client.connect()
    handler = ImageConsumer(
        settings, build_vision_service(settings), MinioFetcher(settings), JsonPublisher(client)
    )
    BaseConsumer(
        client, settings.image_queue, [settings.query_submitted_routing_key], handler.handle
    ).start()


if __name__ == "__main__":
    main()
