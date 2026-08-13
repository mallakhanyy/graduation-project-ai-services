from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.interfaces.chunker import Chunker as ChunkerInterface
from core.value_objects.document_chunk import DocumentChunk
from core.value_objects.loaded_page import LoadedPage


class Chunker(ChunkerInterface):

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def chunk(self, pages: list[LoadedPage], document_id: str) -> list[DocumentChunk]:

        chunks: list[DocumentChunk] = []

        for page in pages:
            split_texts = self.text_splitter.split_text(
                page.content
            )

            for text in split_texts:
                chunk_order = len(chunks)

                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{document_id}_{chunk_order}",
                        text=text,
                        metadata=page.metadata,
                        chunk_order=chunk_order,
                    )
                )

        return chunks