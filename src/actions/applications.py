"""
Application Manager for Context Clock
Handles launching Windows applications.
"""

import os
import subprocess
import logging
import time
from typing import List, Union
import psutil

logger = logging.getLogger(__name__)

class ApplicationManager:
    """Manages launching and monitoring Windows applications."""
    
    def __init__(self):
        """Initialize the application manager."""
        self.launched_apps = []  # Track launched applications
        
    def launch_application(self, app_path: str) -> bool:
        """
        Launch a single application.
        
        Args:
            app_path: Path to the application executable
            
        Returns:
            bool: True if application launched successfully, False otherwise
        """
        try:
            if not self._is_valid_executable(app_path):
                logger.error(f"Invalid executable: {app_path}")
                return False
            
            # Check if application is already running
            app_name = os.path.basename(app_path)
            if self._is_process_running(app_name):
                logger.info(f"Application already running: {app_name}")
                return True
            
            # Launch the application
            logger.info(f"Launching application: {app_path}")
            process = subprocess.Popen(
                app_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
            
            # Give the application time to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                self.launched_apps.append({
                    'path': app_path,
                    'process': process,
                    'name': app_name
                })
                logger.info(f"Application launched successfully: {app_name}")
                return True
            else:
                logger.error(f"Application failed to start or exited immediately: {app_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error launching application {app_path}: {e}")
            return False
    
    def launch_applications(self, app_paths: Union[str, List[str]]) -> List[bool]:
        """
        Launch multiple applications.
        
        Args:
            app_paths: Single app path or list of application paths
            
        Returns:
            list: List of boolean results for each application
        """
        if isinstance(app_paths, str):
            app_paths = [app_paths]
            
        if not app_paths:
            logger.warning("No applications provided to launch")
            return []
            
        results = []
        for app_path in app_paths:
            if app_path and app_path.strip():  # Skip empty paths
                result = self.launch_application(app_path.strip())
                results.append(result)
            else:
                logger.warning("Skipping empty application path")
                results.append(False)
                
        success_count = sum(results)
        logger.info(f"Launched {success_count}/{len(app_paths)} applications successfully")
        
        return results
    
    def _is_valid_executable(self, app_path: str) -> bool:
        """
        Check if the application path is valid.
        
        Args:
            app_path: Path to the application
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(app_path, str) or not app_path.strip():
            return False
            
        if not os.path.exists(app_path):
            logger.warning(f"Application file does not exist: {app_path}")
            return False
            
        if not os.path.isfile(app_path):
            logger.warning(f"Application path is not a file: {app_path}")
            return False
            
        # Check if file is executable
        valid_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.msi'}
        file_extension = os.path.splitext(app_path)[1].lower()
        
        if file_extension not in valid_extensions:
            logger.warning(f"File does not appear to be executable: {app_path}")
            # Don't return False here, as some executables might not have standard extensions
            
        return True
    
    def _is_process_running(self, process_name: str) -> bool:
        """
        Check if a process with the given name is currently running.
        
        Args:
            process_name: Name of the process (with or without .exe)
            
        Returns:
            bool: True if process is running, False otherwise
        """
        try:
            # Ensure process name ends with .exe for consistency
            if not process_name.lower().endswith('.exe'):
                process_name += '.exe'
                
            for process in psutil.process_iter(['name']):
                if process.info['name'] and process.info['name'].lower() == process_name.lower():
                    return True
                    
        except Exception as e:
            logger.debug(f"Error checking if process is running: {e}")
            
        return False
    
    def get_launched_applications(self) -> List[dict]:
        """
        Get list of applications launched by this manager.
        
        Returns:
            list: List of launched application information
        """
        return self.launched_apps.copy()
    
    def cleanup_launched_applications(self):
        """Clean up tracking of launched applications."""
        # Remove processes that are no longer running
        active_apps = []
        for app in self.launched_apps:
            try:
                if app['process'].poll() is None:  # Process still running
                    active_apps.append(app)
                else:
                    logger.debug(f"Process no longer running: {app['name']}")
            except Exception as e:
                logger.debug(f"Error checking process status: {e}")
                
        self.launched_apps = active_apps
    
    def terminate_launched_applications(self):
        """
        Terminate all applications launched by this manager.
        Note: Use with caution as this will forcefully close applications.
        """
        for app in self.launched_apps:
            try:
                if app['process'].poll() is None:  # Process still running
                    logger.info(f"Terminating application: {app['name']}")
                    app['process'].terminate()
                    
                    # Wait for graceful termination
                    try:
                        app['process'].wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't terminate gracefully
                        logger.warning(f"Force killing application: {app['name']}")
                        app['process'].kill()
                        
            except Exception as e:
                logger.error(f"Error terminating application {app['name']}: {e}")
                
        self.launched_apps.clear() 