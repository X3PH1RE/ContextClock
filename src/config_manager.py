"""
Configuration Manager for Context Clock
Handles loading, validation, and management of time block configurations.
"""

import yaml
import os
import logging
from datetime import datetime, time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration loading and validation for Context Clock."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self.config = {}
        self.current_time_block = None
        
    def load_config(self) -> bool:
        """
        Load configuration from YAML file.
        
        Returns:
            bool: True if config loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.config_path):
                logger.error(f"Configuration file not found: {self.config_path}")
                self._create_default_config()
                return False
                
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
                
            if self._validate_config():
                logger.info("Configuration loaded successfully")
                return True
            else:
                logger.error("Configuration validation failed")
                return False
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """
        Validate the loaded configuration.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        if not isinstance(self.config, dict):
            logger.error("Configuration must be a dictionary")
            return False
            
        required_fields = ['start', 'end']
        
        for block_name, block_config in self.config.items():
            if not isinstance(block_config, dict):
                logger.error(f"Time block '{block_name}' must be a dictionary")
                return False
                
            for field in required_fields:
                if field not in block_config:
                    logger.error(f"Time block '{block_name}' missing required field: {field}")
                    return False
                    
            # Validate time format
            try:
                datetime.strptime(block_config['start'], '%H:%M')
                datetime.strptime(block_config['end'], '%H:%M')
            except ValueError as e:
                logger.error(f"Invalid time format in block '{block_name}': {e}")
                return False
                
        return True
    
    def _create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            'morning': {
                'start': '06:00',
                'end': '12:00',
                'wallpaper': 'path/to/morning_wallpaper.jpg',
                'apps': ['notepad.exe'],
                'websites': ['https://google.com'],
                'music': 'path/to/morning_music.mp3'
            },
            'afternoon': {
                'start': '12:00',
                'end': '18:00',
                'wallpaper': 'path/to/afternoon_wallpaper.jpg',
                'apps': [],
                'websites': ['https://github.com'],
                'music': 'path/to/afternoon_music.mp3'
            },
            'evening': {
                'start': '18:00',
                'end': '22:00',
                'wallpaper': 'path/to/evening_wallpaper.jpg',
                'apps': [],
                'websites': [],
                'music': 'path/to/evening_music.mp3'
            },
            'night': {
                'start': '22:00',
                'end': '06:00',
                'wallpaper': 'path/to/night_wallpaper.jpg',
                'apps': [],
                'websites': [],
                'music': 'path/to/night_music.mp3'
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(default_config, file, default_flow_style=False, indent=2)
            logger.info(f"Created default configuration file: {self.config_path}")
        except Exception as e:
            logger.error(f"Error creating default configuration: {e}")
    
    def get_current_time_block(self) -> Optional[str]:
        """
        Get the current time block based on current time.
        
        Returns:
            str: Name of current time block, or None if no match
        """
        current_time = datetime.now().time()
        
        for block_name, block_config in self.config.items():
            start_time = datetime.strptime(block_config['start'], '%H:%M').time()
            end_time = datetime.strptime(block_config['end'], '%H:%M').time()
            
            # Handle time blocks that cross midnight
            if start_time <= end_time:
                # Normal time block (e.g., 09:00 to 17:00)
                if start_time <= current_time < end_time:
                    return block_name
            else:
                # Time block crosses midnight (e.g., 22:00 to 06:00)
                if current_time >= start_time or current_time < end_time:
                    return block_name
                    
        return None
    
    def get_time_block_config(self, block_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific time block.
        
        Args:
            block_name: Name of the time block
            
        Returns:
            dict: Time block configuration, or None if not found
        """
        return self.config.get(block_name)
    
    def get_all_time_blocks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all time block configurations.
        
        Returns:
            dict: All time block configurations
        """
        return self.config.copy()
    
    def set_current_time_block(self, block_name: str):
        """
        Set the current time block (for tracking purposes).
        
        Args:
            block_name: Name of the current time block
        """
        self.current_time_block = block_name
        logger.info(f"Current time block set to: {block_name}") 