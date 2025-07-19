# Context Clock 🕒

A Windows desktop application that automatically adjusts your digital environment based on the time of day. Context Clock runs quietly in the system tray and can change wallpapers, launch applications, open websites, and play music according to your defined time blocks.

## ✨ Features

- **📅 Time Block Management**: Define custom time periods (Morning, Afternoon, Evening, Night)
- **🖼️ Automatic Wallpaper Changes**: Set different wallpapers for each time block
- **🚀 Application Launching**: Automatically start applications when entering time blocks
- **🌐 Website Opening**: Open specific websites in your default browser
- **🎵 Audio Playback**: Play music or ambient sounds for each time period
- **🔧 System Tray Integration**: Minimal interface with pause/resume functionality
- **📝 Easy Configuration**: Simple YAML configuration file
- **🔄 Live Reload**: Update configuration without restarting the application

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.8 or higher

### Installation

1. **Clone or download** this repository:
   ```bash
   git clone <repository-url>
   cd context-clock
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your time blocks** by editing `config.yaml` (see [Configuration](#configuration) section)

4. **Run the application**:
   ```bash
   python main.py
   ```

The application will start in the system tray with a small icon. Right-click the icon to access the menu.

## ⚙️ Configuration

Edit the `config.yaml` file to customize your time blocks and actions:

```yaml
morning:
  start: "06:00"
  end: "12:00"
  wallpaper: "C:/Users/YourName/Pictures/morning_wallpaper.jpg"
  apps:
    - "C:/Program Files/Notion/Notion.exe"
    - "C:/Program Files/Google/Chrome/Application/chrome.exe"
  websites:
    - "https://calendar.google.com"
    - "https://gmail.com"
  music: "C:/Music/morning_playlist.mp3"
```

### Configuration Options

#### Time Blocks
- **start**: Start time in 24-hour format (HH:MM)
- **end**: End time in 24-hour format (HH:MM)
- Time blocks can cross midnight (e.g., "22:00" to "06:00")

#### Actions
- **wallpaper**: 
  - Single file: `"C:/path/to/image.jpg"`
  - Random from folder: `"C:/path/to/wallpapers/"` (ends with / or \\)
- **apps**: List of full paths to executable files
- **websites**: List of URLs (protocol optional - https:// will be added)
- **music**: 
  - Single file: `"C:/path/to/music.mp3"`
  - Random from folder: `"C:/path/to/music/"` (ends with / or \\)

### Supported File Formats

- **Images**: JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
- **Audio**: MP3, WAV, OGG, FLAC, AAC, M4A, WMA
- **Applications**: EXE, BAT, CMD, COM, SCR, MSI

## 🎮 Usage

### System Tray Menu

Right-click the system tray icon to access:

- **Current**: Shows active time block
- **Pause/Resume Automation**: Toggle automation on/off
- **Edit Configuration**: Opens config.yaml in default text editor
- **Reload Configuration**: Reloads settings without restart
- **Show Status**: Opens status window with current information
- **Exit**: Close the application

### Automation Behavior

- **Time Checking**: Every 5 minutes, the app checks if the time block has changed
- **Action Execution**: When entering a new time block, all configured actions run
- **Smart Launching**: Applications already running won't be launched again
- **Audio Management**: Previous audio stops when new audio starts

## 🔧 Building Executable

To create a standalone .exe file:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller --onefile --windowed --icon=icon.ico main.py
   ```

3. **Alternative using the build script**:
   ```bash
   build_exe.bat
   ```

The executable will be created in the `dist/` folder.

## 📁 Project Structure

```
context-clock/
├── main.py                 # Application entry point
├── config.yaml            # Configuration file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── context_clock.py   # Main application logic
│   ├── config_manager.py  # Configuration handling
│   ├── actions/           # Action modules
│   │   ├── wallpaper.py   # Wallpaper management
│   │   ├── applications.py # Application launching
│   │   ├── websites.py    # Website opening
│   │   └── audio.py       # Audio playback
│   └── ui/                # User interface
│       └── system_tray.py # System tray icon
└── logs/                  # Application logs (created automatically)
```

## 🐛 Troubleshooting

### Common Issues

1. **System tray icon not appearing**:
   - Ensure PyQt5 is properly installed
   - Check if system tray is enabled in Windows settings

2. **Wallpaper not changing**:
   - Verify the image file path exists
   - Ensure the image format is supported
   - Check file permissions

3. **Applications not launching**:
   - Verify executable paths are correct
   - Check if applications require administrator privileges
   - Review logs in the `logs/` folder

4. **Audio not playing**:
   - Install pygame: `pip install pygame`
   - Check audio file format and path
   - Verify system audio is working

### Logs

Application logs are saved in the `logs/context_clock.log` file. Check this file for detailed error information.

## 🛡️ Security Notes

- Context Clock only accesses files and applications you explicitly configure
- No network communication except for opening websites you specify
- All actions are logged for transparency
- Configuration file is stored locally and not transmitted anywhere

## 🎨 Customization Ideas

### Advanced Wallpaper Setup
- Create folders with multiple wallpapers for random selection
- Use high-resolution images for best results
- Organize by theme (nature, minimal, abstract, etc.)

### Productivity Workflows
- **Morning**: Email, calendar, news
- **Work Hours**: IDE, documentation, project management tools
- **Break Time**: Music apps, casual websites
- **Evening**: Entertainment, social media

### Audio Ambience
- **Morning**: Upbeat, energizing music
- **Work**: Focus music, ambient sounds
- **Evening**: Relaxing, calming sounds
- **Night**: Sleep sounds, white noise

## 📜 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📧 Support

If you encounter any issues or have questions, please check the logs first and then create an issue with:
- Your configuration file (remove personal paths)
- Relevant log entries
- Steps to reproduce the problem
- Your Windows version and Python version

---

**Enjoy your automated digital environment with Context Clock! 🚀** 