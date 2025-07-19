"""
Context Clock Main Application
Coordinates all components and handles time-based automation.
"""

import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

from .config_manager import ConfigManager
from .ui.system_tray import SystemTrayIcon
from .ui.config_dashboard import ConfigDashboard
from .actions import WallpaperManager, ApplicationManager, WebsiteManager, AudioManager

logger = logging.getLogger(__name__)

class ContextClockApp(QObject):
    """Main Context Clock application coordinating all components."""
    
    # Signals
    time_block_changed = pyqtSignal(str, str)  # new_block, old_block
    
    def __init__(self):
        """Initialize the Context Clock application."""
        super().__init__()
        
        # Configuration
        self.config_manager = ConfigManager()
        
        # Action managers
        self.wallpaper_manager = WallpaperManager()
        self.app_manager = ApplicationManager()
        self.website_manager = WebsiteManager()
        self.audio_manager = AudioManager()
        
        # UI
        self.system_tray = None
        self.config_dashboard = None
        
        # State
        self.automation_enabled = True
        self.current_time_block = None
        self.last_check_time = None
        
        # Timer for periodic checks
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_time_blocks)
        
        # Setup
        self.setup_application()
    
    def setup_application(self):
        """Setup the application components."""
        try:
            # Load configuration
            if not self.config_manager.load_config():
                logger.warning("Failed to load configuration, using default settings")
            
            # Setup system tray
            self.setup_system_tray()
            
            # Setup configuration dashboard
            self.setup_config_dashboard()
            
            # Start periodic time checking
            self.start_time_monitoring()
            
            logger.info("Context Clock application setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up application: {e}")
    
    def setup_system_tray(self):
        """Setup the system tray icon and menu."""
        try:
            self.system_tray = SystemTrayIcon()
            
            # Connect signals
            self.system_tray.automation_toggled.connect(self.set_automation_enabled)
            self.system_tray.exit_requested.connect(self.shutdown)
            self.system_tray.reload_config_requested.connect(self.reload_configuration)
            self.system_tray.dashboard_requested.connect(self.show_config_dashboard)
            self.time_block_changed.connect(self.on_time_block_changed)
            
            logger.info("System tray setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up system tray: {e}")
    
    def setup_config_dashboard(self):
        """Setup the configuration dashboard."""
        try:
            self.config_dashboard = ConfigDashboard(self.config_manager)
            
            # Connect signals
            self.config_dashboard.configChanged.connect(self.on_config_changed)
            
            logger.info("Configuration dashboard setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up configuration dashboard: {e}")
    
    def show_config_dashboard(self):
        """Show the configuration dashboard window."""
        try:
            if self.config_dashboard:
                # Reload latest configuration into dashboard
                self.config_dashboard.load_configuration()
                
                # Show and bring to front
                self.config_dashboard.show()
                self.config_dashboard.raise_()
                self.config_dashboard.activateWindow()
                
                logger.info("Configuration dashboard opened")
                
                # Show notification
                if self.system_tray:
                    self.system_tray.show_notification(
                        "Configuration Dashboard",
                        "Dashboard opened. Make your changes and they'll be saved automatically!",
                        4000
                    )
            else:
                logger.error("Configuration dashboard not initialized")
                
        except Exception as e:
            logger.error(f"Error showing configuration dashboard: {e}")
    
    def on_config_changed(self, new_config: Dict[str, Any]):
        """
        Handle configuration changes from the dashboard.
        
        Args:
            new_config: New configuration dictionary
        """
        try:
            logger.info("Configuration changed via dashboard")
            
            # Update the config manager
            self.config_manager.config = new_config
            
            # Check if we need to execute actions for current time block immediately
            if self.automation_enabled:
                current_block = self.config_manager.get_current_time_block()
                if current_block and current_block != self.current_time_block:
                    # Time block logic changed, update immediately
                    old_block = self.current_time_block
                    self.current_time_block = current_block
                    self.execute_time_block_actions(current_block)
                    self.time_block_changed.emit(current_block, old_block or "None")
                elif current_block == self.current_time_block:
                    # Same time block but configuration changed, re-execute actions
                    self.execute_time_block_actions(current_block)
            
            # Show notification
            if self.system_tray:
                self.system_tray.show_notification(
                    "Configuration Applied",
                    "Your changes have been saved and applied successfully!",
                    3000
                )
            
        except Exception as e:
            logger.error(f"Error handling configuration change: {e}")
    
    def show_tray_icon(self):
        """Show the system tray icon."""
        if self.system_tray:
            self.system_tray.show()
            logger.info("System tray icon shown")
            
            # Show welcome notification
            self.system_tray.show_notification(
                "Context Clock Started",
                "🎉 Context Clock is now running! Right-click the tray icon or double-click to open the configuration dashboard.",
                5000
            )
    
    def start_time_monitoring(self):
        """Start monitoring time blocks."""
        try:
            # Perform initial check
            self.check_time_blocks()
            
            # Start periodic checking every 5 minutes (300,000 ms)
            self.check_timer.start(300000)  # 5 minutes
            
            logger.info("Time monitoring started (checking every 5 minutes)")
            
        except Exception as e:
            logger.error(f"Error starting time monitoring: {e}")
    
    def check_time_blocks(self):
        """Check if the current time block has changed and execute actions."""
        try:
            if not self.automation_enabled:
                logger.debug("Automation disabled, skipping time block check")
                return
            
            # Get current time block
            current_block = self.config_manager.get_current_time_block()
            
            if current_block is None:
                logger.warning("No time block matches current time")
                return
            
            # Check if time block has changed
            if current_block != self.current_time_block:
                old_block = self.current_time_block
                self.current_time_block = current_block
                
                logger.info(f"Time block changed: {old_block} -> {current_block}")
                
                # Execute actions for new time block
                self.execute_time_block_actions(current_block)
                
                # Emit signal
                self.time_block_changed.emit(current_block, old_block or "None")
            else:
                logger.debug(f"Still in time block: {current_block}")
                
        except Exception as e:
            logger.error(f"Error checking time blocks: {e}")
    
    def execute_time_block_actions(self, time_block: str):
        """
        Execute all actions for a specific time block.
        
        Args:
            time_block: Name of the time block
        """
        try:
            block_config = self.config_manager.get_time_block_config(time_block)
            
            if not block_config:
                logger.error(f"No configuration found for time block: {time_block}")
                return
            
            logger.info(f"Executing actions for time block: {time_block}")
            
            # Execute actions in sequence
            self._execute_wallpaper_action(block_config)
            self._execute_applications_action(block_config)
            self._execute_websites_action(block_config)
            self._execute_audio_action(block_config)
            
            # Show notification
            if self.system_tray:
                self.system_tray.show_notification(
                    "Time Block Changed",
                    f"🌅 Switched to {time_block.title()} mode - automation actions executed!",
                    4000
                )
            
            logger.info(f"Completed actions for time block: {time_block}")
            
        except Exception as e:
            logger.error(f"Error executing time block actions: {e}")
    
    def _execute_wallpaper_action(self, block_config: Dict[str, Any]):
        """Execute wallpaper change action."""
        try:
            wallpaper = block_config.get('wallpaper')
            if wallpaper:
                logger.info(f"Changing wallpaper: {wallpaper}")
                
                # Handle folder path for random wallpaper selection
                if wallpaper.endswith(('//', '\\\\')):
                    success = self.wallpaper_manager.set_wallpaper_from_folder(wallpaper)
                else:
                    success = self.wallpaper_manager.set_wallpaper(wallpaper)
                
                if success:
                    logger.info("Wallpaper changed successfully")
                else:
                    logger.warning("Failed to change wallpaper")
            else:
                logger.debug("No wallpaper configured for this time block")
                
        except Exception as e:
            logger.error(f"Error executing wallpaper action: {e}")
    
    def _execute_applications_action(self, block_config: Dict[str, Any]):
        """Execute applications launch action."""
        try:
            apps = block_config.get('apps', [])
            if apps:
                logger.info(f"Launching applications: {apps}")
                results = self.app_manager.launch_applications(apps)
                
                success_count = sum(results)
                logger.info(f"Launched {success_count}/{len(apps)} applications successfully")
            else:
                logger.debug("No applications configured for this time block")
                
        except Exception as e:
            logger.error(f"Error executing applications action: {e}")
    
    def _execute_websites_action(self, block_config: Dict[str, Any]):
        """Execute websites opening action."""
        try:
            websites = block_config.get('websites', [])
            if websites:
                logger.info(f"Opening websites: {websites}")
                results = self.website_manager.open_websites(websites, delay_between_opens=1.5)
                
                success_count = sum(results)
                logger.info(f"Opened {success_count}/{len(websites)} websites successfully")
            else:
                logger.debug("No websites configured for this time block")
                
        except Exception as e:
            logger.error(f"Error executing websites action: {e}")
    
    def _execute_audio_action(self, block_config: Dict[str, Any]):
        """Execute audio playback action."""
        try:
            music = block_config.get('music')
            if music:
                logger.info(f"Playing audio: {music}")
                
                # Stop any currently playing audio first
                self.audio_manager.stop_audio()
                
                # Handle folder path for random audio selection
                if music.endswith(('//', '\\\\')):
                    success = self.audio_manager.play_audio_from_folder(music, loop=False)
                else:
                    success = self.audio_manager.play_audio(music, loop=False)
                
                if success:
                    logger.info("Audio playback started successfully")
                else:
                    logger.warning("Failed to start audio playback")
            else:
                logger.debug("No audio configured for this time block")
                
        except Exception as e:
            logger.error(f"Error executing audio action: {e}")
    
    def on_time_block_changed(self, new_block: str, old_block: str):
        """
        Handle time block change signal.
        
        Args:
            new_block: New time block name
            old_block: Previous time block name
        """
        try:
            # Update system tray
            if self.system_tray:
                self.system_tray.update_time_block(new_block)
            
            # Update config manager
            self.config_manager.set_current_time_block(new_block)
            
            logger.info(f"Time block change handled: {old_block} -> {new_block}")
            
        except Exception as e:
            logger.error(f"Error handling time block change: {e}")
    
    def set_automation_enabled(self, enabled: bool):
        """
        Enable or disable automation.
        
        Args:
            enabled: Whether automation should be enabled
        """
        self.automation_enabled = enabled
        
        if not enabled:
            # Stop any currently playing audio when pausing automation
            self.audio_manager.stop_audio()
            
        logger.info(f"Automation {'enabled' if enabled else 'disabled'}")
    
    def reload_configuration(self):
        """Reload the configuration file."""
        try:
            if self.config_manager.load_config():
                logger.info("Configuration reloaded successfully")
                
                # Reload dashboard if it's open
                if self.config_dashboard and self.config_dashboard.isVisible():
                    self.config_dashboard.load_configuration()
                
                # Check if we need to execute actions for current time block
                if self.automation_enabled:
                    self.check_time_blocks()
                    
                if self.system_tray:
                    self.system_tray.show_notification(
                        "Configuration Reloaded",
                        "Configuration has been reloaded successfully from file!",
                        3000
                    )
            else:
                logger.error("Failed to reload configuration")
                
                if self.system_tray:
                    self.system_tray.show_notification(
                        "Configuration Error",
                        "Failed to reload configuration. Please check your config.yaml file.",
                        4000
                    )
                    
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Get current application status.
        
        Returns:
            dict: Current status information
        """
        return {
            'current_time_block': self.current_time_block,
            'automation_enabled': self.automation_enabled,
            'audio_playing': self.audio_manager.is_audio_playing(),
            'current_audio_file': self.audio_manager.get_current_audio_file(),
            'audio_backend': self.audio_manager.get_audio_backend(),
            'launched_apps': len(self.app_manager.get_launched_applications()),
            'opened_websites': len(self.website_manager.get_opened_websites()),
            'dashboard_open': self.config_dashboard.isVisible() if self.config_dashboard else False
        }
    
    def shutdown(self):
        """Shutdown the application gracefully."""
        try:
            logger.info("Shutting down Context Clock...")
            
            # Stop time monitoring
            if self.check_timer.isActive():
                self.check_timer.stop()
            
            # Stop audio playback
            self.audio_manager.stop_audio()
            
            # Clean up launched applications tracking
            self.app_manager.cleanup_launched_applications()
            
            # Hide and close dashboard
            if self.config_dashboard:
                self.config_dashboard.hide()
                self.config_dashboard.close()
            
            # Hide system tray
            if self.system_tray:
                self.system_tray.hide()
            
            # Quit application
            QApplication.quit()
            
            logger.info("Context Clock shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            # Force quit even if there's an error
            QApplication.quit() 