"""
Website Manager for Context Clock
Handles opening websites in the default web browser.
"""

import webbrowser
import logging
import time
from typing import List, Union
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class WebsiteManager:
    """Manages opening websites in the default web browser."""
    
    def __init__(self):
        """Initialize the website manager."""
        self.opened_urls = []  # Track opened URLs
        
    def open_website(self, url: str) -> bool:
        """
        Open a single website in the default browser.
        
        Args:
            url: URL to open
            
        Returns:
            bool: True if website opened successfully, False otherwise
        """
        try:
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL: {url}")
                return False
            
            # Normalize URL (add protocol if missing)
            normalized_url = self._normalize_url(url)
            
            logger.info(f"Opening website: {normalized_url}")
            
            # Open in default browser
            success = webbrowser.open(normalized_url)
            
            if success:
                self.opened_urls.append(normalized_url)
                logger.info(f"Website opened successfully: {normalized_url}")
                return True
            else:
                logger.error(f"Failed to open website: {normalized_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error opening website {url}: {e}")
            return False
    
    def open_websites(self, urls: Union[str, List[str]], delay_between_opens: float = 1.0) -> List[bool]:
        """
        Open multiple websites in the default browser.
        
        Args:
            urls: Single URL or list of URLs to open
            delay_between_opens: Delay in seconds between opening each website
            
        Returns:
            list: List of boolean results for each website
        """
        if isinstance(urls, str):
            urls = [urls]
            
        if not urls:
            logger.warning("No websites provided to open")
            return []
            
        results = []
        for i, url in enumerate(urls):
            if url and url.strip():  # Skip empty URLs
                result = self.open_website(url.strip())
                results.append(result)
                
                # Add delay between opens to prevent overwhelming the browser
                if i < len(urls) - 1 and delay_between_opens > 0:
                    time.sleep(delay_between_opens)
            else:
                logger.warning("Skipping empty URL")
                results.append(False)
                
        success_count = sum(results)
        logger.info(f"Opened {success_count}/{len(urls)} websites successfully")
        
        return results
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if the URL is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(url, str) or not url.strip():
            return False
            
        # Basic URL validation
        try:
            # Normalize URL for parsing
            normalized_url = self._normalize_url(url)
            result = urlparse(normalized_url)
            
            # Must have scheme and netloc
            if not all([result.scheme, result.netloc]):
                return False
                
            # Check for valid schemes
            valid_schemes = {'http', 'https', 'ftp', 'file'}
            if result.scheme.lower() not in valid_schemes:
                logger.warning(f"Unsupported URL scheme: {result.scheme}")
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"URL validation error: {e}")
            return False
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by adding protocol if missing.
        
        Args:
            url: URL to normalize
            
        Returns:
            str: Normalized URL
        """
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
            # Default to https for web URLs
            if any(url.startswith(prefix) for prefix in ['www.', 'localhost', '127.0.0.1']):
                url = 'https://' + url
            elif '.' in url and not url.startswith(('/', '\\')):
                url = 'https://' + url
            else:
                # For local files or other cases, keep as is
                pass
                
        return url
    
    def open_website_in_new_tab(self, url: str) -> bool:
        """
        Open website in a new tab (if browser supports it).
        
        Args:
            url: URL to open
            
        Returns:
            bool: True if website opened successfully, False otherwise
        """
        try:
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL: {url}")
                return False
            
            normalized_url = self._normalize_url(url)
            
            logger.info(f"Opening website in new tab: {normalized_url}")
            
            # Try to open in new tab
            success = webbrowser.open_new_tab(normalized_url)
            
            if success:
                self.opened_urls.append(normalized_url)
                logger.info(f"Website opened in new tab: {normalized_url}")
                return True
            else:
                # Fallback to regular open
                return self.open_website(url)
                
        except Exception as e:
            logger.error(f"Error opening website in new tab {url}: {e}")
            return False
    
    def open_website_in_new_window(self, url: str) -> bool:
        """
        Open website in a new browser window.
        
        Args:
            url: URL to open
            
        Returns:
            bool: True if website opened successfully, False otherwise
        """
        try:
            if not self._is_valid_url(url):
                logger.error(f"Invalid URL: {url}")
                return False
            
            normalized_url = self._normalize_url(url)
            
            logger.info(f"Opening website in new window: {normalized_url}")
            
            # Try to open in new window
            success = webbrowser.open_new(normalized_url)
            
            if success:
                self.opened_urls.append(normalized_url)
                logger.info(f"Website opened in new window: {normalized_url}")
                return True
            else:
                # Fallback to regular open
                return self.open_website(url)
                
        except Exception as e:
            logger.error(f"Error opening website in new window {url}: {e}")
            return False
    
    def get_opened_websites(self) -> List[str]:
        """
        Get list of websites opened by this manager.
        
        Returns:
            list: List of opened URLs
        """
        return self.opened_urls.copy()
    
    def clear_opened_websites(self):
        """Clear the list of opened websites."""
        self.opened_urls.clear()
        logger.debug("Cleared opened websites list") 