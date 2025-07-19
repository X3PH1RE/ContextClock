"""
System Tray Icon for Context Clock
Provides a minimal system tray interface for the application.
"""

import os
import sys
import logging
import subprocess
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QMessageBox, 
                            QApplication, QWidget, QVBoxLayout, QLabel, 
                            QHBoxLayout, QPushButton, QCheckBox)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap

logger = logging.getLogger(__name__)

class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for Context Clock with context menu and notifications."""
    
    # Signals
    automation_toggled = pyqtSignal(bool)
    exit_requested = pyqtSignal()
    reload_config_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize the system tray icon.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.automation_enabled = True
        self.current_time_block = "Unknown"
        self.setup_icon()
        self.setup_menu()
        self.setup_notifications()
        
        # Connect signals
        self.activated.connect(self.on_tray_icon_activated)
        
    def setup_icon(self):
        """Setup the system tray icon."""
        try:
            # Create a simple icon if no icon file exists
            icon = self.create_default_icon()
            self.setIcon(icon)
            self.setToolTip("Context Clock - Automated Environment Manager")
            
        except Exception as e:
            logger.error(f"Error setting up system tray icon: {e}")
    
    def create_default_icon(self) -> QIcon:
        """
        Create a default icon for the system tray.
        
        Returns:
            QIcon: Default icon
        """
        # Create a simple colored square as default icon
        pixmap = QPixmap(16, 16)
        pixmap.fill()  # Fill with default color
        return QIcon(pixmap)
    
    def setup_menu(self):
        """Setup the context menu for the system tray icon."""
        try:
            self.menu = QMenu()
            
            # Status display
            self.status_action = QAction(f"Current: {self.current_time_block}", self.menu)
            self.status_action.setEnabled(False)
            self.menu.addAction(self.status_action)
            
            self.menu.addSeparator()
            
            # Toggle automation
            self.automation_action = QAction("Pause Automation", self.menu)
            self.automation_action.setCheckable(True)
            self.automation_action.setChecked(False)
            self.automation_action.triggered.connect(self.toggle_automation)
            self.menu.addAction(self.automation_action)
            
            self.menu.addSeparator()
            
            # Edit configuration
            self.edit_config_action = QAction("Edit Configuration", self.menu)
            self.edit_config_action.triggered.connect(self.edit_configuration)
            self.menu.addAction(self.edit_config_action)
            
            # Reload configuration
            self.reload_config_action = QAction("Reload Configuration", self.menu)
            self.reload_config_action.triggered.connect(self.reload_configuration)
            self.menu.addAction(self.reload_config_action)
            
            self.menu.addSeparator()
            
            # Show status window
            self.show_status_action = QAction("Show Status", self.menu)
            self.show_status_action.triggered.connect(self.show_status_window)
            self.menu.addAction(self.show_status_action)
            
            self.menu.addSeparator()
            
            # Exit
            self.exit_action = QAction("Exit", self.menu)
            self.exit_action.triggered.connect(self.exit_application)
            self.menu.addAction(self.exit_action)
            
            self.setContextMenu(self.menu)
            
        except Exception as e:
            logger.error(f"Error setting up system tray menu: {e}")
    
    def setup_notifications(self):
        """Setup notification capabilities."""
        # Check if system tray supports balloon messages
        if not QSystemTrayIcon.supportsMessages():
            logger.warning("System tray does not support balloon messages")
    
    def on_tray_icon_activated(self, reason):
        """
        Handle system tray icon activation.
        
        Args:
            reason: Activation reason
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_status_window()
    
    def toggle_automation(self, checked):
        """
        Toggle automation on/off.
        
        Args:
            checked: Whether automation should be paused
        """
        self.automation_enabled = not checked
        
        if checked:
            self.automation_action.setText("Resume Automation")
            self.show_notification("Automation Paused", "Context Clock automation has been paused.")
        else:
            self.automation_action.setText("Pause Automation")
            self.show_notification("Automation Resumed", "Context Clock automation has been resumed.")
        
        self.automation_toggled.emit(self.automation_enabled)
        logger.info(f"Automation {'enabled' if self.automation_enabled else 'disabled'}")
    
    def edit_configuration(self):
        """Open the configuration file for editing."""
        try:
            config_path = "config.yaml"
            
            if not os.path.exists(config_path):
                self.show_message("Configuration file not found", 
                                f"Configuration file '{config_path}' does not exist.")
                return
            
            # Try to open with default text editor
            if sys.platform.startswith('win'):
                os.startfile(config_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.call(['open', config_path])
            else:  # Linux
                subprocess.call(['xdg-open', config_path])
                
            logger.info("Opened configuration file for editing")
            
        except Exception as e:
            logger.error(f"Error opening configuration file: {e}")
            self.show_message("Error", f"Failed to open configuration file: {e}")
    
    def reload_configuration(self):
        """Request configuration reload."""
        self.show_notification("Configuration", "Reloading configuration...")
        self.reload_config_requested.emit()
        logger.info("Configuration reload requested")
    
    def show_status_window(self):
        """Show a status window with current information."""
        try:
            if hasattr(self, 'status_window') and self.status_window.isVisible():
                self.status_window.raise_()
                self.status_window.activateWindow()
                return
            
            self.status_window = StatusWindow()
            self.status_window.update_status(self.current_time_block, self.automation_enabled)
            self.status_window.show()
            
        except Exception as e:
            logger.error(f"Error showing status window: {e}")
    
    def update_time_block(self, time_block: str):
        """
        Update the current time block display.
        
        Args:
            time_block: Name of the current time block
        """
        self.current_time_block = time_block
        self.status_action.setText(f"Current: {time_block}")
        self.setToolTip(f"Context Clock - Current: {time_block}")
        
        if hasattr(self, 'status_window') and self.status_window.isVisible():
            self.status_window.update_status(time_block, self.automation_enabled)
    
    def show_notification(self, title: str, message: str, duration: int = 3000):
        """
        Show a system tray notification.
        
        Args:
            title: Notification title
            message: Notification message
            duration: Duration in milliseconds
        """
        try:
            if QSystemTrayIcon.supportsMessages():
                self.showMessage(title, message, QSystemTrayIcon.Information, duration)
            else:
                logger.info(f"Notification: {title} - {message}")
                
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def show_message(self, title: str, message: str):
        """
        Show a message box.
        
        Args:
            title: Message title
            message: Message text
        """
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()
    
    def exit_application(self):
        """Exit the application."""
        reply = QMessageBox.question(
            None, 
            "Exit Context Clock",
            "Are you sure you want to exit Context Clock?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.exit_requested.emit()
            logger.info("Exit requested from system tray")


class StatusWindow(QWidget):
    """Simple status window showing current application state."""
    
    def __init__(self):
        """Initialize the status window."""
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Context Clock - Status")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Context Clock Status")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Current time block
        self.time_block_label = QLabel("Current Time Block: Unknown")
        layout.addWidget(self.time_block_label)
        
        # Automation status
        self.automation_label = QLabel("Automation: Enabled")
        layout.addWidget(self.automation_label)
        
        layout.addStretch()
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_status(self, time_block: str, automation_enabled: bool):
        """
        Update the status display.
        
        Args:
            time_block: Current time block
            automation_enabled: Whether automation is enabled
        """
        self.time_block_label.setText(f"Current Time Block: {time_block}")
        
        automation_status = "Enabled" if automation_enabled else "Paused"
        self.automation_label.setText(f"Automation: {automation_status}")
        
        # Update label colors
        if automation_enabled:
            self.automation_label.setStyleSheet("color: green;")
        else:
            self.automation_label.setStyleSheet("color: red;") 