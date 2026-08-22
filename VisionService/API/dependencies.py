"""
Dependency injection for the Vision Service.
"""

from VisionService.Infrastructure.config import Settings, get_settings

# Re-export for convenience
__all__ = ['get_settings', 'Settings']