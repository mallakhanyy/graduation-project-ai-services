"""
model.py
---------
ASR model wrapper for the AI Service.

Responsibilities:
- Load the ASR model once at startup.
- Keep the model in memory.
- Perform speech transcription.

This file should NOT:
- Handle API requests.
- Validate uploaded files.
- Build API responses.
"""

import torch

from qwencleo_asr import QwenCleoASR

from config import settings
from logger import logger


class ASRModel:
    """Wrapper around the QwenCleo ASR engine."""

    def __init__(self):
        self.engine = None
        self.device = None
        self.is_loaded = False

        self._load_model()

    def _load_model(self):
        """Load the ASR model into memory."""

        logger.info("Loading ASR model...")

        try:
            # --------------------------------------------------
            # Select device
            # --------------------------------------------------
            if settings.model.device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = settings.model.device

            logger.info(f"Using device: {self.device}")

            # --------------------------------------------------
            # Load model
            # --------------------------------------------------
            #
            # QwenCleoASR loads:
            # - model
            # - processor
            # internally.
            #
            self.engine = QwenCleoASR(device=self.device)

            self.is_loaded = True

            logger.info("ASR model loaded successfully.")

        except Exception as e:
            logger.critical(f"Failed to load ASR model: {e}")
            raise

    def transcribe(
        self,
        audio_path: str,
        language: str = "Arabic",
    ) -> str:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to audio file.
            language: Language hint.

        Returns:
            Transcript text.
        """

        if not self.is_loaded:
            raise RuntimeError("ASR model is not loaded.")

        logger.info(f"Starting transcription: {audio_path}")

        try:

            result = self.engine.transcribe(
                audio_path,
                language=language,
            )

            transcript = result.text

            logger.info("Transcription completed successfully.")

            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise


# ==========================================================
# Global Model Instance
# ==========================================================

asr_model = ASRModel()