from application.services.context_builder_service import ContextBuilderService
from core.value_objects.retrieved_chunk import RetrievedChunk


def main():

    chunks = [
        RetrievedChunk(
            chunk_id="chunk-001",
            text="Drainage problems can cause water accumulation.",
            metadata={"source": "test.pdf"},
            score=0.83,
        ),
        RetrievedChunk(
            chunk_id="chunk-002",
            text="Rainwater harvesting can reduce water waste.",
            metadata={"source": "test.pdf"},
            score=0.67,
        ),
    ]

    service = ContextBuilderService()

    context = service.build(chunks)

    print("\nGenerated Context:\n")
    print(context)


if __name__ == "__main__":
    main()