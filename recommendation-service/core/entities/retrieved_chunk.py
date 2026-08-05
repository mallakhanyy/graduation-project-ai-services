from dataclasses import dataclass

@dataclass
class RetrievedChunk:
    chunk_id : str
    document_name : str
    page_number : int
    text : str
    similarity_score : float