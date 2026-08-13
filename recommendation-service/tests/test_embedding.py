from infrastructure.embeddings.bge_m3_embedding import BGEM3EmbeddingService


def main():
    embedding_service = BGEM3EmbeddingService()

    text = "Rainwater harvesting can improve water availability."

    embedding = embedding_service.embed(text)

    print(f"Embedding dimensions: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")


if __name__ == "__main__":
    main()