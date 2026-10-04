"""
Interfaces for testing and abstraction.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class IPredictor(ABC):
    """Interface for prediction services."""
    
    @abstractmethod
    def predict(self, image_path: str) -> Dict[str, Any]:
        """Predict problem from image."""
        pass

class ISeverityCalculator(ABC):
    """Interface for severity calculation."""
    
    @abstractmethod
    def calculate(self, problem: str, confidence: float) -> str:
        """Calculate severity level."""
        pass