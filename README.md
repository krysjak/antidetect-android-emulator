# AntiDetect Android Emulator

A Windows-oriented Python toolchain that wraps the official Android SDK `emulator.exe`, generates a unique synthetic device identity per run, and applies **multi-layer anti-detection** — at boot/config level (AVD `config.ini` + ADB `setprop`), at the hardware layer (IMEI/MAC/GPU/sensors/battery), and at runtime (Frida hooks on the Java API, native `libc`, and Google attestation).

> ⚠️ **Educational / research project.** Frida hooking, SafetyNet/Play Integrity forging, and identity spoofing touch anti-fraud systems. Use only on devices and accounts you own or are authorized to test. Hardware-key attestation cannot truly be defeated — the included `safetynet_bypass.js` forges the JWS result and passes basic checks only.

---

## ✨ Features

### 🔑 Synthetic identity generation (`profile_generator.py`)
Every device gets a full, internally-consistent identity:
- **Luhn-valid 15-digit IMEI** (+ `imei2` for dual-SIM) using real TAC prefixes per brand (Samsung, Xiaomi, Pixel, Huawei).
- Brand-specific **serial numbers** (Samsung `R5CT…`, Xiaomi 16-char, Pixel 12-char, OnePlus `NB…`).
- 16-hex **Android ID**, **GSF ID**, UUIDv4 **advertising ID**.
- Three **MAC addresses** (Wi-Fi, Bluetooth, generic) using **real vendor OUI prefixes** per brand.
- 3–8 realistic nearby **Wi-Fi SSIDs** (NETGEAR/TP-LINK/ASUS with `_5G`/`_Guest` suffixes).
- 50+ real-device profiles (`device_profiles.py`) with genuine model/device/board/build-fingerprint strings.

### 🛡️ Three-tier spoofing
1. **Boot / config (`spoof/system_*.py`)**
   - Per-partition props (`ro.product.{system,vendor,odm,product,system_ext}.*`) — a commonly-missed detection vector.
   - Emulator indicators zeroed: `ro.kernel.qemu=0`, `ro.boot.qemu=0`, `ro.hardware=ranchu`, goldfish audio emptied.
   - `SystemSpoofer`: `adb root` + `remount`, build props, hide emulator strings.
2. **Hardware (`spoof/hardware_spoof.py`, `gpu_spoof.py`, `sensor_simulator.py`, `battery_spoof.py`)**
   - IMEI via `service call iphonesubinfo`, serial, android_id, file hiding.
   - **GPU**: real OpenGL ES renderer strings (Mali-G720, Adreno 740/750, Mali-G715) per model.
   - **Sensors**: threaded daemon with `idle` / `pocket` / `hand` motion modes to defeat static-sensor detection.
   - **Battery**: flagship/midrange/budget profiles with time-varying telemetry.
3. **Runtime Frida hooks (`frida/scripts/*.js`)**
   - `anti_detect.js` (565 lines) — `Build`, `TelephonyManager` (IMEI/IMSI/MEID/number/SIM serial), `Settings$Secure`, `File.exists()` (18-entry emulator-path blacklist).
   - `native_hooks.js` (380 lines) — libc-level interception, 31-entry file blacklist, `/proc/cpuinfo` rewriting (`QEMU Virtual CPU` → `Qualcomm Kryo 585`, etc.).
   - `safetynet_bypass.js` (334 lines) — forges SafetyNet/Play Integrity JWS attestation results.

### 🌐 Anonymity
- `ProxyManager` supports HTTP and SOCKS5 proxies, wired into the emulator via `-http-proxy`.

---

## 🏗️ Architecture

```
main.py (Click CLI)            gui/app.py (Flask + SocketIO dashboard)
   │
   ▼
core/device_manager.py ── DeviceManager: create/list/launch/stop, AVD config.ini,
   │                        system+hardware+Frida spoofing orchestration
   └── core/hook_manager.py ── HookManager: Frida session lifecycle

spoof/   → SystemSpoofer, HardwareSpoofer, GPUSpoofer, SensorSimulator, BatterySpoofer
profiles/→ profile_generator (identity), device_profiles (50+ real models)
frida/   → FridaHooks (inject), FridaServerManager (auto-download frida-server 16.1.4),
           scripts/anti_detect.js, native_hooks.js, safetynet_bypass.js
anonymity/ → ProxyManager (HTTP/SOCKS5)
```

Generated device identities are saved as JSON under `data/devices/` (gitignored).

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+**
- **Android SDK** with `emulator.exe`, `adb.exe`, `avdmanager`, `sdkmanager`. The default SDK path is `C:\Users\<user>\AppData\Local\Android\Sdk` (overridable in `config.py`).
- **Root** on the emulator (required for `service call` IMEI spoofing and `ro.*` props).
- **Frida server** on the device — `FridaServerManager` auto-downloads `frida-server-16.1.4` for `android-x86_64`, pushes it to `/data/local/tmp/`, and starts it.

### Install
```bash
pip install -r requirements.txt
```

### Usage (Click CLI)
```bash
python main.py check_sdk                                        # verify SDK/ADB
python main.py models                                           # list 50+ phone models
python main.py create -m "Samsung Galaxy S24" -a 14             # create device
python main.py create -m "Samsung Galaxy S24" -a 14 -p socks5://127.0.0.1:1080
python main.py list                                             # list saved devices
python main.py launch <name> --frida                            # launch + runtime hooks
python main.py stop <name>
python main.py gui                                              # web dashboard (:8080)

# Apply spoofing to an already-running emulator:
python apply_antidetect.py -s emulator-5554 -m "Samsung Galaxy S24 Ultra"
python update_devices.py                                        # re-apply props to AVDs
```

### Web GUI
`python main.py gui` starts a Flask + Flask-SocketIO dashboard at `http://127.0.0.1:8080` with REST endpoints under `/api/...` for device CRUD, launch, stop, and model listing.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask`, `flask-socketio`, `eventlet` | Web dashboard + real-time updates |
| `frida-tools` | Runtime hook injection |
| `adb-shell` | ADB communication |
| `click` | CLI framework |
| `pyyaml` | Config parsing |
| `colorama` | Colored terminal output |
| `pysocks` | SOCKS5 proxy support |
| `requests` | HTTP (frida-server download) |

---

## ⚠️ Known Limitations

- **Windows-first** — paths use `C:\...` and `.exe`/`.bat` binaries; cross-platform use requires editing `config.py`.
- **Hardware attestation** — `safetynet_bypass.js` forges the JWS result and passes basic software checks, but strict key-backed Play Integrity attestation cannot be truly defeated.
- Frida hooks target the Java API and libc; apps using native obfuscation or custom detection may still fingerprint the device.

---

## 📁 Project Structure

```
android-emulator/
├── main.py                  # Click CLI entry
├── config.py                # SDK paths, Android versions, defaults
├── apply_antidetect.py      # Standalone spoofing for running emulators
├── update_devices.py        # Re-apply props to existing AVDs
├── core/                    # device_manager, hook_manager
├── spoof/                   # system, hardware, gpu, sensor, battery spoofers
├── profiles/                # identity + 50+ real device profiles
├── frida/                   # FridaHooks, server manager, JS scripts
├── anonymity/               # ProxyManager
└── gui/                     # Flask + SocketIO dashboard
```
