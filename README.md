# AntiDetect Android Emulator

Anonymous Android phone emulator with anti-detection features.

## Features

- 🖥️ **Web GUI Dashboard** - BlueStacks-style interface
- 📱 **50+ Phone Models** - Samsung, Xiaomi, Pixel, OnePlus, Huawei
- 🔄 **Android 9-14** - Multiple Android versions support
- 🕵️ **Anti-Detection** - System props, hardware IDs, sensors spoofing
- 🔒 **Anonymity** - Proxy/VPN integration, no telemetry

## Requirements

- Python 3.8+
- Android SDK with emulator
- ADB in PATH

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Start GUI dashboard
python main.py gui

# CLI: Create new device
python main.py create --model "Samsung Galaxy S24" --android 14

# CLI: List devices
python main.py list

# CLI: Launch device
python main.py launch --name mydevice
```

## License

For educational and security testing purposes only.
