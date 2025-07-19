"""
Wallpaper Manager for Context Clock
Handles changing Windows desktop wallpaper.
"""

import os
import ctypes
import logging
import random
from typing import Union, List
from ctypes import wintypes

logger = logging.getLogger(__name__)

class WallpaperManager:
    """Manages desktop wallpaper changes on Windows."""
    
    # Windows API constants
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    
    def __init__(self):
        """Initialize the wallpaper manager."""
        self.user32 = ctypes.windll.user32
        
    def set_wallpaper(self, wallpaper_path: Union[str, List[str]]) -> bool:
        """
        Set the desktop wallpaper.
        
        Args:
            wallpaper_path: Path to wallpaper image or list of paths for random selection
            
        Returns:
            bool: True if wallpaper was set successfully, False otherwise
        """
        try:
            # Handle list of wallpapers (random selection)
            if isinstance(wallpaper_path, list):
                if not wallpaper_path:
                    logger.warning("Empty wallpaper list provided")
                    return False
                    
                # Filter valid image files
                valid_paths = [path for path in wallpaper_path if self._is_valid_image_file(path)]
                
                if not valid_paths:
                    logger.error("No valid image files found in wallpaper list")
                    return False
                    
                wallpaper_path = random.choice(valid_paths)
                logger.info(f"Selected random wallpaper: {wallpaper_path}")
            
            # Validate single wallpaper path
            if not self._is_valid_image_file(wallpaper_path):
                logger.error(f"Invalid wallpaper file: {wallpaper_path}")
                return False
            
            # Convert to absolute path
            abs_path = os.path.abspath(wallpaper_path)
            
            # Set wallpaper using Windows API
            result = self.user32.SystemParametersInfoW(
                self.SPI_SETDESKWALLPAPER,
                0,
                abs_path,
                self.SPIF_UPDATEINIFILE | self.SPIF_SENDCHANGE
            )
            
            if result:
                logger.info(f"Wallpaper set successfully: {abs_path}")
                return True
            else:
                logger.error(f"Failed to set wallpaper: {abs_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting wallpaper: {e}")
            return False
    
    def _is_valid_image_file(self, file_path: str) -> bool:
        """
        Check if the file is a valid image file.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not isinstance(file_path, str):
            return False
            
        if not os.path.exists(file_path):
            logger.warning(f"Wallpaper file does not exist: {file_path}")
            return False
            
        if not os.path.isfile(file_path):
            logger.warning(f"Wallpaper path is not a file: {file_path}")
            return False
            
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in valid_extensions:
            logger.warning(f"Unsupported image format: {file_extension}")
            return False
            
        return True
    
    def get_wallpapers_from_folder(self, folder_path: str) -> List[str]:
        """
        Get all valid wallpaper files from a folder.
        
        Args:
            folder_path: Path to folder containing wallpapers
            
        Returns:
            list: List of valid wallpaper file paths
        """
        wallpapers = []
        
        try:
            if not os.path.exists(folder_path):
                logger.warning(f"Wallpaper folder does not exist: {folder_path}")
                return wallpapers
                
            if not os.path.isdir(folder_path):
                logger.warning(f"Wallpaper path is not a directory: {folder_path}")
                return wallpapers
                
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if self._is_valid_image_file(file_path):
                    wallpapers.append(file_path)
                    
            logger.info(f"Found {len(wallpapers)} wallpapers in folder: {folder_path}")
            
        except Exception as e:
            logger.error(f"Error scanning wallpaper folder: {e}")
            
        return wallpapers
    
    def set_wallpaper_from_folder(self, folder_path: str) -> bool:
        """
        Set a random wallpaper from a folder.
        
        Args:
            folder_path: Path to folder containing wallpapers
            
        Returns:
            bool: True if wallpaper was set successfully, False otherwise
        """
        wallpapers = self.get_wallpapers_from_folder(folder_path)
        
        if not wallpapers:
            logger.error(f"No valid wallpapers found in folder: {folder_path}")
            return False
            
        return self.set_wallpaper(wallpapers) 