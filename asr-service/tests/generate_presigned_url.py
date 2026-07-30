from datetime import timedelta

from minio import Minio


client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)

url = client.presigned_get_object(
    "asr-audio",
    "9_256_cropped.flac",
    expires=timedelta(minutes=60),
)

print("Presigned URL:")
print(url)