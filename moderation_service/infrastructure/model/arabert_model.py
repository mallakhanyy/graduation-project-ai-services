"""AraBERT model implementation."""

import time
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple, Dict, Optional, List, Any

from app.core.exceptions import ModelLoadError, ModelPredictionError
from app.core.config import settings
from app.core.logger import logger
from app.services.interfaces.model_service_interface import ModelService


class AraBERTModel(ModelService):
    """AraBERT model implementation."""
    
    def __init__(self) -> None:
        """Initialize model service."""
        self._tokenizer: Optional[AutoTokenizer] = None
        self._model: Optional[AutoModelForSequenceClassification] = None
        self._device = torch.device(
            "cuda" if settings.device == "cuda" and torch.cuda.is_available() else "cpu"
        )
        # Label mapping
        self._label_mapping: dict[int, str] = {
            0: "Relevant",
            1: "Spam",
            2: "Offensive",
            3: "Irrelevant",
        }
        self._loaded: bool = False
    
    def load(self) -> None:
        """Load the model and tokenizer."""
        try:
            logger.info(f"Loading model from {settings.model_path} on {self._device}")
            
            self._tokenizer = AutoTokenizer.from_pretrained(settings.model_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                settings.model_path
            )
            self._model.to(self._device)
            self._model.eval()
            
            self._loaded = True
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise ModelLoadError(f"Failed to load model: {str(e)}", {"error": str(e)})
    
    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """Predict label for text."""
        if not self._loaded:
            self.load()
        
        if not self._loaded:
            raise ModelLoadError("Model is not loaded")
        
        if not text or not text.strip():
            raise ModelPredictionError("Empty text provided for prediction")
        
        try:
            start_time = time.time()
            
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=settings.max_sequence_length,
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=1)
            
            pred_id = int(torch.argmax(logits, dim=1).item())
            confidence = float(probabilities[0, pred_id].item())
            label = self._label_mapping.get(pred_id, "Unknown")
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.debug(
                f"Prediction: '{text[:50]}...' -> {label} ({confidence:.2%}) in {processing_time:.2f}ms"
            )
            
            # Return empty dict instead of all_scores
            return label, confidence, {}
            
        except Exception as e:
            raise ModelPredictionError(f"Prediction failed: {str(e)}")
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float, Dict[str, float]]]:
        """Predict labels for multiple texts."""
        if not self._loaded:
            self.load()
        
        if not texts:
            return []
        
        try:
            inputs = self._tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=settings.max_sequence_length,
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self._model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=1)
            
            results = []
            pred_ids = torch.argmax(logits, dim=1).cpu().numpy()
            
            for i, pred_id in enumerate(pred_ids):
                confidence = float(probabilities[i, pred_id].item())
                label = self._label_mapping.get(pred_id, "Unknown")
                # Return empty dict instead of all_scores
                results.append((label, confidence, {}))
            
            return results
        except Exception as e:
            raise ModelPredictionError(f"Batch prediction failed: {str(e)}")
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    def get_device(self) -> str:
        return str(self._device)
    
    def get_label_mapping(self) -> Dict[int, str]:
        return self._label_mapping.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        info = {
            "loaded": self._loaded,
            "device": self.get_device(),
            "model_path": settings.model_path,
            "labels": list(self._label_mapping.values()),
            "num_labels": len(self._label_mapping),
        }
        return info