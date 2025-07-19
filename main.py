#!/usr/bin/env python3
"""
Context Clock - Main Entry Point
A Windows desktop application that automatically adjusts your digital environment based on time of day.
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QDateTime
from src.context_clock import ContextClockApp

def setup_logging():
    """Setup logging configuration."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'context_clock.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create QApplication instance
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # Keep running when main window is closed
        
        # Create and start the Context Clock app
        context_clock = ContextClockApp()
        context_clock.show_tray_icon()
        
        logger.info("Context Clock started successfully")
        
        # Start the application event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Failed to start Context Clock: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 