"""Interface for model service abstraction."""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Any


class ModelService(ABC):
    """
    Abstract interface for model services.
    
    This interface defines the contract that all model services must implement.
    It allows for easy swapping of different model implementations.
    """
    
    @abstractmethod
    def load(self) -> None:
        """
        Load the model from disk.
        
        Raises:
            ModelLoadError: If model fails to load.
        """
        pass
    
    @abstractmethod
    def predict(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Predict the label for a given text.
        
        Args:
            text: Text to classify.
            
        Returns:
            Tuple containing:
                - label: Predicted label
                - confidence: Confidence score
                - all_scores: Dictionary of all class probabilities
                
        Raises:
            ModelPredictionError: If prediction fails.
        """
        pass
    
    @abstractmethod
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float, Dict[str, float]]]:
        """
        Predict labels for multiple texts in batch.
        
        Args:
            texts: List of texts to classify.
            
        Returns:
            List of tuples (label, confidence, all_scores) for each text.
            
        Raises:
            ModelPredictionError: If batch prediction fails.
        """
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """
        Check if the model is loaded.
        
        Returns:
            True if model is loaded, False otherwise.
        """
        pass
    
    @abstractmethod
    def get_device(self) -> str:
        """
        Get the device the model is running on.
        
        Returns:
            Device string (e.g., "cpu", "cuda:0").
        """
        pass
    
    @abstractmethod
    def get_label_mapping(self) -> Dict[int, str]:
        """
        Get the label mapping.
        
        Returns:
            Dictionary mapping integer labels to string labels.
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information.
        """
        pass