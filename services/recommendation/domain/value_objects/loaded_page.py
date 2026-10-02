from dataclasses import dataclass
from typing import Any


@dataclass
class LoadedPage:
    content: str
    page_number: int
    metadata: dict[str, Any]
    