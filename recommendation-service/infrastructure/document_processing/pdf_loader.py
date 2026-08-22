from io import BytesIO

from pypdf import PdfReader

from core.value_objects.loaded_page import LoadedPage


class PDFLoader:

    def load(
        self,
        file_bytes: bytes,
        document_id: str,
    ) -> list[LoadedPage]:

        reader = PdfReader(BytesIO(file_bytes))

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            content = page.extract_text() or ""

            pages.append(
                LoadedPage(
                    content=content,
                    page_number=page_number,
                    metadata={
                        "document_id": document_id,
                        "page_number": page_number,
                    },
                )
            )

        return pages