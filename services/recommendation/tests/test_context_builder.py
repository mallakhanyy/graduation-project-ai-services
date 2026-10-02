import pytest

from application.services.context_builder_service import ContextBuilderService
from core.value_objects.retrieved_chunk import RetrievedChunk


def test_context_builder_includes_relevant_metadata():
    chunks = [
        RetrievedChunk(
            chunk_id="chunk-001",
            text="Drainage problems can cause water accumulation.",
            metadata={
                "document_id": "rainwater_manual.pdf",
                "page_number": 7,
            },
            score=0.83,
        )
    ]

    service = ContextBuilderService()

    context = service.build(chunks)

    assert "rainwater_manual.pdf" in context
    assert "Page: 7" in context
    assert "Drainage problems can cause water accumulation." in context

    # Internal retrieval details should not be sent to the LLM
    assert "chunk-001" not in context
    assert "0.83" not in context


def test_context_builder_returns_empty_for_no_chunks():
    service = ContextBuilderService()

    assert service.build([]) == ""
