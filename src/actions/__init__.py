"""
Context Clock Actions Package
Contains modules for different automation actions.
"""

from .wallpaper import WallpaperManager
from .applications import ApplicationManager
from .websites import WebsiteManager
from .audio import AudioManager

__all__ = ['WallpaperManager', 'ApplicationManager', 'WebsiteManager', 'AudioManager'] 