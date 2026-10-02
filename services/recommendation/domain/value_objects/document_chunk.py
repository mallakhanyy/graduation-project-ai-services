from dataclasses import dataclass
from typing import Any


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    chunk_order: int