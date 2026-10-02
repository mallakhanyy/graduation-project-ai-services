from infrastructure.storage.minio_storage import MinIOStorage


def main():
    storage = MinIOStorage()

    object_key = "t0234e.pdf"

    file_bytes = storage.download(object_key)

    print(f"Downloaded {len(file_bytes)} bytes")


if __name__ == "__main__":
    main()