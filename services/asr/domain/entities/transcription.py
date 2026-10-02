from enum import Enum
from dataclasses import dataclass

class TranscriptionStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

@dataclass
class Transcription:
    request_id : str
    status : TranscriptionStatus = TranscriptionStatus.PENDING
    text : str | None = None
    processing_time : float | None = None
    error : str | None = None

    def start_processing(self) -> None:

        if self.status != TranscriptionStatus.PENDING:
            raise ValueError(
                "Transcription must be pending to start processing"
            )
        
        self.status = TranscriptionStatus.PROCESSING

    def complete(
        self, 
        text: str, 
        processing_time: float
    ) -> None:

        if self.status != TranscriptionStatus.PROCESSING:
            raise ValueError(
                "Transcription must be processing to complete processing"
            )
        
        self.status = TranscriptionStatus.COMPLETED
        self.text = text
        self.processing_time = processing_time
        self.error = None


    def fail(
        self, 
        error: str, 
        processing_time: float
    ) -> None:
        
        if self.status != TranscriptionStatus.PROCESSING:
            raise ValueError(
                "Transcription must be processing to fail processing"
            )
        
        self.status = TranscriptionStatus.FAILED
        self.text = None
        self.error = error
        self.processing_time = processing_time