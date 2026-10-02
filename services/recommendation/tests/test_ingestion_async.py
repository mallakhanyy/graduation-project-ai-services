import pytest
from unittest.mock import AsyncMock, MagicMock
from application.services.document_ingestion_service import DocumentIngestionService
from core.value_objects.document_chunk import DocumentChunk


@pytest.mark.asyncio
async def test_document_ingestion_async_flow():
    # 1. Arrange Mocks
    mock_storage = MagicMock()
    mock_loader = MagicMock()
    mock_chunker = MagicMock()
    mock_chunk_repository = AsyncMock()
    mock_embedding_service = MagicMock()
    mock_vector_store = AsyncMock()

    # محاكاة تحميل ملف PDF وهمي
    mock_storage.download.return_value = b"%PDF-1.4 mock content"
    
    # استخدام MagicMock للـ LoadedPage لتجنب مشاكل الـ constructor fields
    mock_page = MagicMock()
    mock_loader.load.return_value = [mock_page]

    mock_chunk = DocumentChunk(
        chunk_id="chunk-test-1",
        text="Helwan AI sample text",
        metadata={
            "document_id": "test_doc.pdf",
            "page_number": 1,
        },
        chunk_order=0,
    )
    mock_chunker.chunk.return_value = [mock_chunk]
    
    mock_embedding_service.embed_many.return_value = [[0.1, 0.2, 0.3, 0.4]]

    service = DocumentIngestionService(
        storage=mock_storage,
        loader=mock_loader,
        chunker=mock_chunker,
        chunk_repository=mock_chunk_repository,
        embedding_service=mock_embedding_service,
        vector_store=mock_vector_store
    )

    # 2. Act
    await service.ingest(object_key="test_doc.pdf")

    # 3. Assert
    mock_storage.download.assert_called_once_with("test_doc.pdf")
    mock_loader.load.assert_called_once_with(
        b"%PDF-1.4 mock content",
        "test_doc.pdf",
    )
    mock_chunker.chunk.assert_called_once()
    created_chunk = mock_chunker.chunk.return_value[0]
    assert created_chunk.metadata["document_id"] == "test_doc.pdf"
    assert created_chunk.metadata["page_number"] == 1
    mock_chunk_repository.save_many.assert_awaited_once()
    mock_embedding_service.embed_many.assert_called_once()
    mock_vector_store.add.assert_awaited_once()