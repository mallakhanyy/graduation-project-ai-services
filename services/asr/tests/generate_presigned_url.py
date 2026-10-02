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
    "AUDIO_FILE = '/home/mallakhanyy/Projects/ai-services/dataset/audio_files/9_28_cropped.flac'",
    expires=timedelta(minutes=60),
)

print("Presigned URL:")
print(url)