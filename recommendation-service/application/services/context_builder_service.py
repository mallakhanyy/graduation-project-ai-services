from core.value_objects.retrieved_chunk import RetrievedChunk


class ContextBuilderService:

    def build(
        self,
        chunks: list[RetrievedChunk],
    ) -> str:

        if not chunks:
            return ""

        context_parts = []

        for index, chunk in enumerate(chunks, start=1):

            document_id = chunk.metadata.get(
                "document_id",
                "unknown",
            )

            page_number = chunk.metadata.get(
                "page_number",
                "unknown",
            )

            context_parts.append(
                f"""[Context {index}]
                    Source: {document_id}
                    Page: {page_number}
                    Text:
                    {chunk.text}
                """
            )

        return "\n".join(context_parts)