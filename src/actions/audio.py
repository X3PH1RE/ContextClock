"""
Audio Manager for Context Clock
Handles playing music and sound files.
"""

import os
import logging
import threading
import time
from typing import Optional, List, Union
import random

# Try to import pygame for audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    
# Fallback to playsound if pygame is not available
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages audio playback for Context Clock."""
    
    def __init__(self):
        """Initialize the audio manager."""
        self.current_audio_thread = None
        self.is_playing = False
        self.should_stop = False
        self.current_file = None
        
        # Initialize pygame mixer if available
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.audio_backend = 'pygame'
                logger.info("Audio backend: pygame")
            except Exception as e:
                logger.warning(f"Failed to initialize pygame mixer: {e}")
                self.audio_backend = 'playsound' if PLAYSOUND_AVAILABLE else None
        elif PLAYSOUND_AVAILABLE:
            self.audio_backend = 'playsound'
            logger.info("Audio backend: playsound")
        else:
            self.audio_backend = None
            logger.warning("No audio backend available. Audio features will be disabled.")
    
    def play_audio(self, audio_path: Union[str, List[str]], loop: bool = False) -> bool:
        """
        Play an audio file.
        
        Args:
            audio_path: Path to audio file or list of paths for random selection
            loop: Whether to loop the audio continuously
            
        Returns:
            bool: True if audio started playing successfully, False otherwise
        """
        if self.audio_backend is None:
            logger.warning("No audio backend available - skipping audio playback")
            return False
        
        try:
            # Handle list of audio files (random selection)
            if isinstance(audio_path, list):
                if not audio_path:
                    logger.warning("Empty audio list provided")
                    return False
                    
                # Filter valid audio files
                valid_paths = [path for path in audio_path if self._is_valid_audio_file(path)]
                
                if not valid_paths:
                    logger.error("No valid audio files found in list")
                    return False
                    
                audio_path = random.choice(valid_paths)
                logger.info(f"Selected random audio: {audio_path}")
            
            # Validate single audio path
            if not self._is_valid_audio_file(audio_path):
                logger.error(f"Invalid audio file: {audio_path}")
                return False
            
            # Stop any currently playing audio
            self.stop_audio()
            
            # Start playing audio in a separate thread
            self.current_file = audio_path
            self.should_stop = False
            self.current_audio_thread = threading.Thread(
                target=self._play_audio_thread,
                args=(audio_path, loop),
                daemon=True
            )
            self.current_audio_thread.start()
            
            logger.info(f"Started playing audio: {audio_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio {audio_path}: {e}")
            return False
    
    def _play_audio_thread(self, audio_path: str, loop: bool):
        """
        Audio playback thread function.
        
        Args:
            audio_path: Path to audio file
            loop: Whether to loop the audio
        """
        try:
            self.is_playing = True
            
            if self.audio_backend == 'pygame':
                self._play_with_pygame(audio_path, loop)
            elif self.audio_backend == 'playsound':
                self._play_with_playsound(audio_path, loop)
                
        except Exception as e:
            logger.error(f"Error in audio playback thread: {e}")
        finally:
            self.is_playing = False
            self.current_file = None
    
    def _play_with_pygame(self, audio_path: str, loop: bool):
        """
        Play audio using pygame.
        
        Args:
            audio_path: Path to audio file
            loop: Whether to loop the audio
        """
        try:
            pygame.mixer.music.load(audio_path)
            
            # Play audio (loop = -1 means infinite loop, 0 means play once)
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops)
            
            # Wait for playback to finish or stop signal
            while pygame.mixer.music.get_busy() and not self.should_stop:
                time.sleep(0.1)
                
            if self.should_stop:
                pygame.mixer.music.stop()
                
        except Exception as e:
            logger.error(f"Error playing audio with pygame: {e}")
    
    def _play_with_playsound(self, audio_path: str, loop: bool):
        """
        Play audio using playsound.
        
        Args:
            audio_path: Path to audio file
            loop: Whether to loop the audio
        """
        try:
            if not PLAYSOUND_AVAILABLE:
                logger.error("Playsound not available")
                return
                
            if loop:
                # Simple loop implementation for playsound
                while not self.should_stop:
                    playsound(audio_path, block=True)
                    if self.should_stop:
                        break
            else:
                playsound(audio_path, block=True)
                
        except Exception as e:
            logger.error(f"Error playing audio with playsound: {e}")
    
    def stop_audio(self):
        """Stop any currently playing audio."""
        try:
            if self.is_playing:
                self.should_stop = True
                
                if self.audio_backend == 'pygame' and PYGAME_AVAILABLE:
                    pygame.mixer.music.stop()
                
                # Wait for audio thread to finish
                if self.current_audio_thread and self.current_audio_thread.is_alive():
                    self.current_audio_thread.join(timeout=2.0)
                
                logger.info("Audio playback stopped")
                
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    
    def _is_valid_audio_file(self, file_path: str) -> bool:
        """
        Check if the file is a valid audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        if not isinstance(file_path, str):
            return False
            
        if not os.path.exists(file_path):
            logger.warning(f"Audio file does not exist: {file_path}")
            return False
            
        if not os.path.isfile(file_path):
            logger.warning(f"Audio path is not a file: {file_path}")
            return False
            
        # Check file extension
        valid_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.wma'}
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension not in valid_extensions:
            logger.warning(f"Unsupported audio format: {file_extension}")
            return False
            
        return True
    
    def get_audio_files_from_folder(self, folder_path: str) -> List[str]:
        """
        Get all valid audio files from a folder.
        
        Args:
            folder_path: Path to folder containing audio files
            
        Returns:
            list: List of valid audio file paths
        """
        audio_files = []
        
        try:
            if not os.path.exists(folder_path):
                logger.warning(f"Audio folder does not exist: {folder_path}")
                return audio_files
                
            if not os.path.isdir(folder_path):
                logger.warning(f"Audio path is not a directory: {folder_path}")
                return audio_files
                
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if self._is_valid_audio_file(file_path):
                    audio_files.append(file_path)
                    
            logger.info(f"Found {len(audio_files)} audio files in folder: {folder_path}")
            
        except Exception as e:
            logger.error(f"Error scanning audio folder: {e}")
            
        return audio_files
    
    def play_audio_from_folder(self, folder_path: str, loop: bool = False) -> bool:
        """
        Play a random audio file from a folder.
        
        Args:
            folder_path: Path to folder containing audio files
            loop: Whether to loop the selected audio
            
        Returns:
            bool: True if audio started playing successfully, False otherwise
        """
        audio_files = self.get_audio_files_from_folder(folder_path)
        
        if not audio_files:
            logger.error(f"No valid audio files found in folder: {folder_path}")
            return False
            
        return self.play_audio(audio_files, loop)
    
    def is_audio_playing(self) -> bool:
        """
        Check if audio is currently playing.
        
        Returns:
            bool: True if audio is playing, False otherwise
        """
        return self.is_playing
    
    def get_current_audio_file(self) -> Optional[str]:
        """
        Get the path of the currently playing audio file.
        
        Returns:
            str: Path to current audio file, or None if not playing
        """
        return self.current_file
    
    def get_audio_backend(self) -> Optional[str]:
        """
        Get the current audio backend being used.
        
        Returns:
            str: Name of audio backend, or None if not available
        """
        return self.audio_backend 