from sentence_transformers import SentenceTransformer

from core.interfaces.embedding_service import EmbeddingService
from shared.config import get_settings


class BGEM3EmbeddingService(EmbeddingService):

    def __init__(self):
        settings = get_settings()

        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL_NAME
        )

        self.normalize_embeddings = settings.EMBEDDING_NORMALIZE

        self.dimension = self.model.get_embedding_dimension()

    def embed(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=self.normalize_embeddings,
        )

        return embedding.tolist()

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=self.normalize_embeddings,
        )

        return embeddings.tolist()