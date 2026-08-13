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

            context_parts.append(
                f"""[Context {index}]
                Chunk ID: {chunk.chunk_id}
                Score: {chunk.score}
                Metadata: {chunk.metadata}
                Text:
                {chunk.text}
                """
            )

        return "\n".join(context_parts)