import time
import torch
from qwencleo_asr import QwenCleoASR
from core.interfaces.asr_model import ASRModel
from core.value_objects.asr_result import ASRResult
from shared.logger import logger


class QwenASR(ASRModel):

    def __init__(self):
        self.engine = None
        self._load_model()


    def _load_model(self) -> None:
        logger.info("Loading Qwen ASR model...")
        try:
            self.engine = QwenCleoASR(
                device = "cuda" if torch.cuda.is_available() else "cpu"
            )

            logger.info("Qwen ASR model loaded successfully.")

        except Exception as e:
            logger.error(
                f"Failed to load Qwen ASR model: {e}"
            )
            raise RuntimeError(
                "Failed to load ASR Model"
            )from e
        

    def transcribe(self, audio_path: str) -> ASRResult:

        if self.engine is None:
            raise RuntimeError(
                "Failed to load ASR Model"
            )
        
        logger.info(
            f"Starting transcription: {audio_path}"
        )

        try:
             result = self.engine.transcribe(
                  audio_path
             )

             logger.info(
                 "Transcription completed successfully."
             )

             return ASRResult(
                  text = result.text,
             )

        except Exception as e:
            logger.error(
                f"Transcription failed: {e}"
            )
            raise