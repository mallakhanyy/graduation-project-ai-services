from minio import Minio

from core.interfaces.file_storage import FileStorage
from shared.config import get_settings


class MinIOStorage(FileStorage):

    def __init__(self):
        settings = get_settings()

        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

        self.bucket_name = settings.MINIO_BUCKET_NAME

    def download(self, object_key: str) -> bytes:
        response = self.client.get_object(
            self.bucket_name,
            object_key,
        )

        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()