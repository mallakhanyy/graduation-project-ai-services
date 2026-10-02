from dataclasses import dataclass
from typing import Any


@dataclass
class Document:
    document_id: str
    file_name: str
    file_type: str
    metadata: dict[str, Any]