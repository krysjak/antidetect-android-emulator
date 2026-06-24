"""
AntiDetect Android Emulator - Configuration
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PROFILES_DIR = DATA_DIR / "profiles"
SAVED_DEVICES_DIR = DATA_DIR / "devices"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
SAVED_DEVICES_DIR.mkdir(exist_ok=True)

# Android SDK settings
ANDROID_SDK_ROOT = r"C:\Users\admin\AppData\Local\Android\Sdk"
EMULATOR_PATH = os.path.join(ANDROID_SDK_ROOT, "emulator", "emulator.exe")
ADB_PATH = os.path.join(ANDROID_SDK_ROOT, "platform-tools", "adb.exe")
AVDMANAGER_PATH = os.path.join(ANDROID_SDK_ROOT, "cmdline-tools", "latest", "bin", "avdmanager.bat")
SDKMANAGER_PATH = os.path.join(ANDROID_SDK_ROOT, "cmdline-tools", "latest", "bin", "sdkmanager.bat")

# GUI settings
GUI_HOST = "127.0.0.1"
GUI_PORT = 8080

# Android versions supported
ANDROID_VERSIONS = {
    "9": {"api": 28, "codename": "Pie", "image": "system-images;android-28;google_apis_playstore;x86_64"},
    "10": {"api": 29, "codename": "Q", "image": "system-images;android-29;google_apis_playstore;x86_64"},
    "11": {"api": 30, "codename": "R", "image": "system-images;android-30;google_apis_playstore;x86_64"},
    "12": {"api": 31, "codename": "S", "image": "system-images;android-31;google_apis_playstore;x86_64"},
    "13": {"api": 33, "codename": "Tiramisu", "image": "system-images;android-33;google_apis_playstore;x86_64"},
    "14": {"api": 34, "codename": "UpsideDownCake", "image": "system-images;android-34;google_apis_playstore;x86_64"},
}

# Default emulator settings
DEFAULT_RAM = 4096  # MB
DEFAULT_HEAP = 512  # MB
DEFAULT_CORES = 4

# Anti-detection settings
HIDE_ROOT = True
SPOOF_SENSORS = True
MASK_FILESYSTEM = True
