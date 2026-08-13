import asyncio

from core.value_objects.document_chunk import DocumentChunk
from infrastructure.persistence.mongodb.mongodb_client import MongoDBClient
from infrastructure.persistence.mongodb.chunk_repository import MongoChunkRepository


async def main():
    mongodb_client = MongoDBClient()
    repository = MongoChunkRepository(mongodb_client)

    chunks = [
        DocumentChunk(
            chunk_id="test-002",
            text="First chunk of the document.",
            metadata={
                "document_id": "test-document-002",
                "file_name": "test.pdf",
                "page_number": 1,
            },
            chunk_order=0,
        ),
        DocumentChunk(
            chunk_id="test-003",
            text="Second chunk of the document.",
            metadata={
                "document_id": "test-document-002",
                "file_name": "test.pdf",
                "page_number": 1,
            },
            chunk_order=1,
        ),
        DocumentChunk(
            chunk_id="test-004",
            text="Third chunk of the document.",
            metadata={
                "document_id": "test-document-002",
                "file_name": "test.pdf",
                "page_number": 2,
            },
            chunk_order=2,
        ),
    ]

    await repository.save_many(chunks)

    retrieved_chunks = await repository.get_by_document_id(
        "test-document-002"
    )

    print(f"Retrieved {len(retrieved_chunks)} chunks")

    for chunk in retrieved_chunks:
        print(chunk)

    mongodb_client.close()


if __name__ == "__main__":
    asyncio.run(main())