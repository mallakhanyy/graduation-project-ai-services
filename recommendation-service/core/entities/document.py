from dataclasses import dataclass
from typing import Optional

@dataclass
class Document:
    document_id : str
    title : str
    source : str
    language : Optional[str] = None