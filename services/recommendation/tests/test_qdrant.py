from infrastructure.persistence.qdrant.qdrant_client import QdrantClient


def main():
    qdrant_client = QdrantClient()

    collections = qdrant_client.get_client().get_collections()

    print("Qdrant connection successful!")
    print(collections)

    qdrant_client.close()


if __name__ == "__main__":
    main()