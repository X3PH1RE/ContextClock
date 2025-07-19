"""
Configuration Dashboard for Context Clock
Beautiful GUI for managing time blocks and automation settings.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QTimeEdit, QFileDialog, QMessageBox, QTextEdit, QCheckBox,
    QScrollArea, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
    QComboBox, QSlider, QSpinBox, QProgressBar, QSplitter
)
from PyQt5.QtCore import Qt, QTime, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

logger = logging.getLogger(__name__)

class ModernTimeEdit(QWidget):
    """Modern time picker widget with AM/PM display."""
    
    timeChanged = pyqtSignal(str)
    
    def __init__(self, time_str="09:00"):
        super().__init__()
        self.setup_ui()
        self.set_time(time_str)
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background: white;
            }
            QTimeEdit:focus {
                border-color: #4CAF50;
            }
        """)
        
        self.time_edit.timeChanged.connect(self._on_time_changed)
        
        self.am_pm_label = QLabel("AM")
        self.am_pm_label.setStyleSheet("""
            QLabel {
                background: #f5f5f5;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                color: #666;
                min-width: 30px;
                text-align: center;
            }
        """)
        
        layout.addWidget(self.time_edit)
        layout.addWidget(self.am_pm_label)
        self.setLayout(layout)
    
    def _on_time_changed(self):
        time = self.time_edit.time()
        time_str = time.toString("HH:mm")
        
        # Update AM/PM indicator
        hour = time.hour()
        if hour == 0:
            self.am_pm_label.setText("12 AM")
        elif hour < 12:
            self.am_pm_label.setText(f"{hour} AM")
        elif hour == 12:
            self.am_pm_label.setText("12 PM")
        else:
            self.am_pm_label.setText(f"{hour-12} PM")
        
        self.timeChanged.emit(time_str)
    
    def set_time(self, time_str: str):
        """Set time from string format HH:MM"""
        try:
            time = QTime.fromString(time_str, "HH:mm")
            self.time_edit.setTime(time)
        except:
            self.time_edit.setTime(QTime(9, 0))
    
    def get_time(self) -> str:
        """Get time as string in HH:MM format"""
        return self.time_edit.time().toString("HH:mm")

class FilePickerWidget(QWidget):
    """Modern file picker with preview and browse button."""
    
    fileChanged = pyqtSignal(str)
    
    def __init__(self, file_type="file", file_filter="All Files (*)"):
        super().__init__()
        self.file_type = file_type  # "file" or "folder"
        self.file_filter = file_filter
        self.current_path = ""
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Path display
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(f"Select {self.file_type}...")
        self.path_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        self.path_edit.textChanged.connect(self._on_path_changed)
        
        # Browse button
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
        self.browse_btn.clicked.connect(self._browse_file)
        
        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                font-size: 16px;
                min-width: 30px;
                max-width: 30px;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        self.clear_btn.clicked.connect(self._clear_path)
        
        layout.addWidget(self.path_edit, 1)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.clear_btn)
        self.setLayout(layout)
    
    def _browse_file(self):
        if self.file_type == "folder":
            path = QFileDialog.getExistingDirectory(
                self, f"Select Folder", 
                os.path.expanduser("~")
            )
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, f"Select File",
                os.path.expanduser("~"),
                self.file_filter
            )
        
        if path:
            self.set_path(path)
    
    def _clear_path(self):
        self.set_path("")
    
    def _on_path_changed(self):
        self.current_path = self.path_edit.text()
        self.fileChanged.emit(self.current_path)
    
    def set_path(self, path: str):
        self.current_path = path
        self.path_edit.setText(path)
    
    def get_path(self) -> str:
        return self.current_path

class TimeBlockWidget(QWidget):
    """Widget for editing a single time block configuration."""
    
    blockChanged = pyqtSignal(str, dict)  # block_name, config
    deleteRequested = pyqtSignal(str)     # block_name
    
    def __init__(self, block_name: str, config: Dict[str, Any]):
        super().__init__()
        self.block_name = block_name
        self.config = config.copy()
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        # Main container with modern styling
        self.setStyleSheet("""
            TimeBlockWidget {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with time block name and controls
        header_layout = QHBoxLayout()
        
        # Time block name
        name_label = QLabel(self.block_name.title())
        name_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }
        """)
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Delete this time block")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 16px;
                min-width: 40px;
            }
            QPushButton:hover {
                background: #d32f2f;
            }
        """)
        delete_btn.clicked.connect(lambda: self.deleteRequested.emit(self.block_name))
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(delete_btn)
        
        # Time settings
        time_group = self.create_time_section()
        
        # Actions sections
        actions_splitter = QSplitter(Qt.Horizontal)
        
        # Left column
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.addWidget(self.create_wallpaper_section())
        left_layout.addWidget(self.create_audio_section())
        
        # Right column  
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.addWidget(self.create_apps_section())
        right_layout.addWidget(self.create_websites_section())
        
        actions_splitter.addWidget(left_column)
        actions_splitter.addWidget(right_column)
        actions_splitter.setSizes([1, 1])  # Equal width
        
        layout.addLayout(header_layout)
        layout.addWidget(time_group)
        layout.addWidget(actions_splitter)
        
        self.setLayout(layout)
    
    def create_time_section(self):
        group = QGroupBox("⏰ Time Range")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: white;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Start time
        start_layout = QVBoxLayout()
        start_layout.addWidget(QLabel("Start Time:"))
        self.start_time = ModernTimeEdit()
        self.start_time.timeChanged.connect(self._on_config_changed)
        start_layout.addWidget(self.start_time)
        
        # End time
        end_layout = QVBoxLayout()
        end_layout.addWidget(QLabel("End Time:"))
        self.end_time = ModernTimeEdit()
        self.end_time.timeChanged.connect(self._on_config_changed)
        end_layout.addWidget(self.end_time)
        
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_wallpaper_section(self):
        group = QGroupBox("🖼️ Wallpaper")
        group.setStyleSheet(self._get_group_style())
        
        layout = QVBoxLayout()
        
        self.wallpaper_picker = FilePickerWidget(
            "file", 
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp)"
        )
        self.wallpaper_picker.fileChanged.connect(self._on_config_changed)
        
        # Option for random wallpapers from folder
        self.wallpaper_folder_picker = FilePickerWidget("folder")
        self.wallpaper_folder_picker.fileChanged.connect(self._on_config_changed)
        
        self.wallpaper_mode = QComboBox()
        self.wallpaper_mode.addItems(["Single Image", "Random from Folder"])
        self.wallpaper_mode.setStyleSheet("""
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background: white;
            }
        """)
        self.wallpaper_mode.currentTextChanged.connect(self._on_wallpaper_mode_changed)
        
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.wallpaper_mode)
        layout.addWidget(QLabel("Image File:"))
        layout.addWidget(self.wallpaper_picker)
        layout.addWidget(QLabel("Or Folder:"))
        layout.addWidget(self.wallpaper_folder_picker)
        
        group.setLayout(layout)
        return group
    
    def create_audio_section(self):
        group = QGroupBox("🎵 Audio")
        group.setStyleSheet(self._get_group_style())
        
        layout = QVBoxLayout()
        
        self.audio_picker = FilePickerWidget(
            "file",
            "Audio (*.mp3 *.wav *.ogg *.flac *.aac *.m4a *.wma)"
        )
        self.audio_picker.fileChanged.connect(self._on_config_changed)
        
        self.audio_folder_picker = FilePickerWidget("folder")
        self.audio_folder_picker.fileChanged.connect(self._on_config_changed)
        
        self.audio_mode = QComboBox()
        self.audio_mode.addItems(["Single File", "Random from Folder", "No Audio"])
        self.audio_mode.setStyleSheet("""
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                background: white;
            }
        """)
        self.audio_mode.currentTextChanged.connect(self._on_audio_mode_changed)
        
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.audio_mode)
        layout.addWidget(QLabel("Audio File:"))
        layout.addWidget(self.audio_picker)
        layout.addWidget(QLabel("Or Folder:"))
        layout.addWidget(self.audio_folder_picker)
        
        group.setLayout(layout)
        return group
    
    def create_apps_section(self):
        group = QGroupBox("🚀 Applications")
        group.setStyleSheet(self._get_group_style())
        
        layout = QVBoxLayout()
        
        # Apps list
        self.apps_list = QListWidget()
        self.apps_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        # Add app controls
        add_layout = QHBoxLayout()
        
        add_app_btn = QPushButton("+ Add App")
        add_app_btn.setStyleSheet(self._get_button_style("#2196F3", "#1976D2"))
        add_app_btn.clicked.connect(self._add_application)
        
        remove_app_btn = QPushButton("- Remove")
        remove_app_btn.setStyleSheet(self._get_button_style("#f44336", "#d32f2f"))
        remove_app_btn.clicked.connect(self._remove_selected_app)
        
        add_layout.addWidget(add_app_btn)
        add_layout.addWidget(remove_app_btn)
        add_layout.addStretch()
        
        layout.addWidget(self.apps_list)
        layout.addLayout(add_layout)
        
        group.setLayout(layout)
        return group
    
    def create_websites_section(self):
        group = QGroupBox("🌐 Websites")
        group.setStyleSheet(self._get_group_style())
        
        layout = QVBoxLayout()
        
        # Websites list
        self.websites_list = QListWidget()
        self.websites_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: #e8f5e8;
                color: #2e7d32;
            }
        """)
        
        # Add website controls
        add_layout = QVBoxLayout()
        
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("Enter website URL (e.g., https://spotify.com)")
        self.website_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4CAF50;
            }
        """)
        
        website_btn_layout = QHBoxLayout()
        
        add_website_btn = QPushButton("+ Add Website")
        add_website_btn.setStyleSheet(self._get_button_style("#4CAF50", "#45a049"))
        add_website_btn.clicked.connect(self._add_website)
        
        remove_website_btn = QPushButton("- Remove")
        remove_website_btn.setStyleSheet(self._get_button_style("#f44336", "#d32f2f"))
        remove_website_btn.clicked.connect(self._remove_selected_website)
        
        website_btn_layout.addWidget(add_website_btn)
        website_btn_layout.addWidget(remove_website_btn)
        website_btn_layout.addStretch()
        
        add_layout.addWidget(self.website_input)
        add_layout.addLayout(website_btn_layout)
        
        layout.addWidget(self.websites_list)
        layout.addLayout(add_layout)
        
        group.setLayout(layout)
        return group
    
    def _get_group_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background: white;
            }
        """
    
    def _get_button_style(self, bg_color, hover_color):
        return f"""
            QPushButton {{
                background: {bg_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
        """
    
    def _on_wallpaper_mode_changed(self):
        mode = self.wallpaper_mode.currentText()
        if mode == "Single Image":
            self.wallpaper_picker.setVisible(True)
            self.wallpaper_folder_picker.setVisible(False)
        else:
            self.wallpaper_picker.setVisible(False)
            self.wallpaper_folder_picker.setVisible(True)
        self._on_config_changed()
    
    def _on_audio_mode_changed(self):
        mode = self.audio_mode.currentText()
        if mode == "Single File":
            self.audio_picker.setVisible(True)
            self.audio_folder_picker.setVisible(False)
        elif mode == "Random from Folder":
            self.audio_picker.setVisible(False)
            self.audio_folder_picker.setVisible(True)
        else:  # No Audio
            self.audio_picker.setVisible(False)
            self.audio_folder_picker.setVisible(False)
        self._on_config_changed()
    
    def _add_application(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Application",
            "C:/Program Files",
            "Executables (*.exe *.bat *.cmd *.com *.scr *.msi)"
        )
        
        if file_path:
            self.apps_list.addItem(file_path)
            self._on_config_changed()
    
    def _remove_selected_app(self):
        current_row = self.apps_list.currentRow()
        if current_row >= 0:
            self.apps_list.takeItem(current_row)
            self._on_config_changed()
    
    def _add_website(self):
        url = self.website_input.text().strip()
        if url:
            # Add https:// if no protocol specified
            if not url.startswith(('http://', 'https://', 'ftp://')):
                url = 'https://' + url
            
            self.websites_list.addItem(url)
            self.website_input.clear()
            self._on_config_changed()
    
    def _remove_selected_website(self):
        current_row = self.websites_list.currentRow()
        if current_row >= 0:
            self.websites_list.takeItem(current_row)
            self._on_config_changed()
    
    def _on_config_changed(self):
        """Update config when any setting changes"""
        self.save_config()
        self.blockChanged.emit(self.block_name, self.config)
    
    def load_config(self):
        """Load configuration into UI elements"""
        # Time settings
        self.start_time.set_time(self.config.get('start', '09:00'))
        self.end_time.set_time(self.config.get('end', '17:00'))
        
        # Wallpaper settings
        wallpaper = self.config.get('wallpaper', '')
        if wallpaper.endswith(('//', '\\\\')):
            self.wallpaper_mode.setCurrentText("Random from Folder")
            self.wallpaper_folder_picker.set_path(wallpaper)
        else:
            self.wallpaper_mode.setCurrentText("Single Image")
            self.wallpaper_picker.set_path(wallpaper)
        
        # Audio settings
        music = self.config.get('music', '')
        if not music:
            self.audio_mode.setCurrentText("No Audio")
        elif music.endswith(('//', '\\\\')):
            self.audio_mode.setCurrentText("Random from Folder")
            self.audio_folder_picker.set_path(music)
        else:
            self.audio_mode.setCurrentText("Single File")
            self.audio_picker.set_path(music)
        
        # Applications
        apps = self.config.get('apps', [])
        for app in apps:
            if app.strip():
                self.apps_list.addItem(app)
        
        # Websites
        websites = self.config.get('websites', [])
        for website in websites:
            if website.strip():
                self.websites_list.addItem(website)
    
    def save_config(self):
        """Save current UI state to config"""
        self.config['start'] = self.start_time.get_time()
        self.config['end'] = self.end_time.get_time()
        
        # Wallpaper
        if self.wallpaper_mode.currentText() == "Single Image":
            self.config['wallpaper'] = self.wallpaper_picker.get_path()
        else:
            folder = self.wallpaper_folder_picker.get_path()
            if folder and not folder.endswith(('//', '\\\\')):
                folder += '/'
            self.config['wallpaper'] = folder
        
        # Audio
        if self.audio_mode.currentText() == "No Audio":
            self.config['music'] = ''
        elif self.audio_mode.currentText() == "Single File":
            self.config['music'] = self.audio_picker.get_path()
        else:
            folder = self.audio_folder_picker.get_path()
            if folder and not folder.endswith(('//', '\\\\')):
                folder += '/'
            self.config['music'] = folder
        
        # Applications
        apps = []
        for i in range(self.apps_list.count()):
            apps.append(self.apps_list.item(i).text())
        self.config['apps'] = apps
        
        # Websites
        websites = []
        for i in range(self.websites_list.count()):
            websites.append(self.websites_list.item(i).text())
        self.config['websites'] = websites

class ConfigDashboard(QWidget):
    """Main configuration dashboard window."""
    
    configChanged = pyqtSignal(dict)  # Emitted when config changes
    
    def __init__(self, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.time_blocks = {}
        self.setup_ui()
        self.load_configuration()
    
    def setup_ui(self):
        self.setWindowTitle("Context Clock - Configuration Dashboard")
        self.setGeometry(200, 200, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Modern window styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content area
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(20)
        
        content_scroll.setWidget(self.content_widget)
        layout.addWidget(content_scroll, 1)
        
        # Footer with save/cancel buttons
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
    
    def create_header(self):
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("⚙️ Context Clock Configuration")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: transparent;
            }
        """)
        
        # Add time block button
        add_block_btn = QPushButton("+ Add Time Block")
        add_block_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        add_block_btn.clicked.connect(self._add_time_block)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(add_block_btn)
        
        header.setLayout(layout)
        return header
    
    def create_footer(self):
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 15px;
                border: 2px solid #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
            }
        """)
        
        # Auto-save indicator
        self.autosave_label = QLabel("✓ Auto-save enabled")
        self.autosave_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Buttons
        save_btn = QPushButton("💾 Save & Apply")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #45a049;
            }
        """)
        save_btn.clicked.connect(self._save_configuration)
        
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #ff9800;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #f57c00;
            }
        """)
        reset_btn.clicked.connect(self._reset_configuration)
        
        close_btn = QPushButton("✕ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #757575;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #616161;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.autosave_label)
        layout.addStretch()
        layout.addWidget(reset_btn)
        layout.addWidget(save_btn)
        layout.addWidget(close_btn)
        
        footer.setLayout(layout)
        return footer
    
    def load_configuration(self):
        """Load configuration from config manager"""
        if not self.config_manager:
            return
        
        config = self.config_manager.get_all_time_blocks()
        
        # Clear existing time blocks
        self._clear_time_blocks()
        
        # Add time blocks from config
        for block_name, block_config in config.items():
            self._add_time_block_widget(block_name, block_config)
    
    def _clear_time_blocks(self):
        """Clear all time block widgets"""
        for widget in self.time_blocks.values():
            widget.setParent(None)
        self.time_blocks.clear()
    
    def _add_time_block_widget(self, block_name: str, config: Dict[str, Any]):
        """Add a time block widget to the UI"""
        widget = TimeBlockWidget(block_name, config)
        widget.blockChanged.connect(self._on_block_changed)
        widget.deleteRequested.connect(self._delete_time_block)
        
        self.time_blocks[block_name] = widget
        self.content_layout.addWidget(widget)
        
        self.status_label.setText(f"Loaded time block: {block_name}")
    
    def _add_time_block(self):
        """Add a new time block"""
        from PyQt5.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, "Add Time Block", 
            "Enter time block name:"
        )
        
        if ok and name.strip():
            name = name.strip().lower()
            if name in self.time_blocks:
                QMessageBox.warning(self, "Error", "Time block already exists!")
                return
            
            # Default configuration
            default_config = {
                'start': '09:00',
                'end': '17:00',
                'wallpaper': '',
                'apps': [],
                'websites': [],
                'music': ''
            }
            
            self._add_time_block_widget(name, default_config)
            self.status_label.setText(f"Added new time block: {name}")
    
    def _delete_time_block(self, block_name: str):
        """Delete a time block"""
        reply = QMessageBox.question(
            self, "Delete Time Block",
            f"Are you sure you want to delete '{block_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if block_name in self.time_blocks:
                self.time_blocks[block_name].setParent(None)
                del self.time_blocks[block_name]
                self.status_label.setText(f"Deleted time block: {block_name}")
    
    def _on_block_changed(self, block_name: str, config: Dict[str, Any]):
        """Handle time block configuration changes"""
        self.status_label.setText(f"Updated: {block_name}")
        
        # Auto-save after a short delay
        if hasattr(self, '_autosave_timer'):
            self._autosave_timer.stop()
        
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._auto_save)
        self._autosave_timer.setSingleShot(True)
        self._autosave_timer.start(1000)  # Auto-save after 1 second
    
    def _auto_save(self):
        """Auto-save configuration"""
        try:
            self._save_configuration()
            self.autosave_label.setText("✓ Auto-saved")
            self.autosave_label.setStyleSheet("QLabel { color: #4CAF50; font-size: 12px; font-weight: bold; }")
        except Exception as e:
            self.autosave_label.setText("✗ Auto-save failed")
            self.autosave_label.setStyleSheet("QLabel { color: #f44336; font-size: 12px; font-weight: bold; }")
            logger.error(f"Auto-save failed: {e}")
    
    def _save_configuration(self):
        """Save current configuration"""
        if not self.config_manager:
            return
        
        # Collect configuration from all time blocks
        config = {}
        for block_name, widget in self.time_blocks.items():
            widget.save_config()
            config[block_name] = widget.config
        
        # Update config manager
        self.config_manager.config = config
        
        # Save to file
        try:
            import yaml
            with open(self.config_manager.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, indent=2)
            
            self.status_label.setText("Configuration saved successfully!")
            self.configChanged.emit(config)
            
            # Show success message briefly
            QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))
            
        except Exception as e:
            self.status_label.setText(f"Save failed: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration:\n{e}")
    
    def _reset_configuration(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, "Reset Configuration",
            "Are you sure you want to reset to default configuration?\nThis will delete all your current settings.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.config_manager:
                self.config_manager._create_default_config()
                self.config_manager.load_config()
                self.load_configuration()
                self.status_label.setText("Configuration reset to defaults")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Auto-save before closing
        try:
            self._save_configuration()
        except:
            pass
        super().closeEvent(event) 