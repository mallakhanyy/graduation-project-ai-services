from abc import ABC, abstractmethod
from domain.value_objects.asr_result import ASRResult

class ASRModel(ABC):

    @abstractmethod
    def transcribe(
        self, 
        audio_path: str
    ) -> ASRResult:
        pass
