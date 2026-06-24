"""
Device Manager - Create, launch, and manage emulator devices
"""
import json
import os
import subprocess
import uuid
from pathlib import Path
from datetime import datetime

import config
from profiles.device_profiles import get_model_profile
from profiles.profile_generator import generate_device_identity
from spoof.system_props import generate_props_config


class DeviceManager:
    """Manages emulator device lifecycle"""
    
    def __init__(self):
        self.devices_dir = config.SAVED_DEVICES_DIR
        self.devices_dir.mkdir(parents=True, exist_ok=True)
        self._running_processes = {}
    
    def list_devices(self):
        """List all saved devices"""
        devices = []
        for device_file in self.devices_dir.glob("*.json"):
            try:
                with open(device_file, "r", encoding="utf-8") as f:
                    device = json.load(f)
                    device["running"] = self._is_running(device["name"])
                    devices.append(device)
            except Exception:
                continue
        return sorted(devices, key=lambda x: x.get("created", ""), reverse=True)
    
    def get_device(self, name):
        """Get device by name"""
        device_file = self.devices_dir / f"{name}.json"
        if not device_file.exists():
            return None
        with open(device_file, "r", encoding="utf-8") as f:
            device = json.load(f)
            device["running"] = self._is_running(name)
            return device
    
    def create_device(self, model, android_version="14", name=None, proxy=None):
        """Create a new device with anti-detection profile"""
        
        # Get model profile
        model_profile = get_model_profile(model)
        if not model_profile:
            raise ValueError(f"Unknown model: {model}. Use 'models' command to see available models.")
        
        # Generate unique identity
        identity = generate_device_identity(model_profile)
        
        # Generate unique name if not provided
        if not name:
            name = f"{model_profile['brand'].lower()}_{uuid.uuid4().hex[:6]}"
        
        # Validate Android version
        if android_version not in config.ANDROID_VERSIONS:
            raise ValueError(f"Unsupported Android version: {android_version}")
        
        android_info = config.ANDROID_VERSIONS[android_version]
        
        # Create device config
        device = {
            "name": name,
            "model": model,
            "brand": model_profile["brand"],
            "android_version": android_version,
            "api_level": android_info["api"],
            "codename": android_info["codename"],
            "proxy": proxy,
            "identity": identity,
            "created": datetime.now().isoformat(),
            "avd_name": f"antidetect_{name}",
        }
        
        # Create AVD
        self._create_avd(device, android_info)
        
        # Save device config
        device_file = self.devices_dir / f"{name}.json"
        with open(device_file, "w", encoding="utf-8") as f:
            json.dump(device, f, indent=2)
        
        return device
    
    def _create_avd(self, device, android_info):
        """Create Android Virtual Device"""
        avd_name = device["avd_name"]
        
        # Check if system image is installed
        # In real implementation, would download if missing
        
        # Create AVD using avdmanager
        cmd = [
            config.AVDMANAGER_PATH,
            "create", "avd",
            "--name", avd_name,
            "--package", android_info["image"],
            "--device", "pixel_6",
            "--force"
        ]
        
        try:
            # Note: This requires Android SDK to be properly installed
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input="no\n",  # Don't create custom hardware profile
                timeout=60
            )
            if result.returncode != 0:
                print(f"AVD creation warning: {result.stderr}")
        except FileNotFoundError:
            # SDK not found - will create config files manually
            self._create_avd_config_manually(device, android_info)
        except Exception as e:
            print(f"AVD creation notice: {e}")
            self._create_avd_config_manually(device, android_info)
    
    def _create_avd_config_manually(self, device, android_info):
        """Create AVD config files manually when SDK tools unavailable"""
        avd_path = Path.home() / ".android" / "avd" / f"{device['avd_name']}.avd"
        avd_path.mkdir(parents=True, exist_ok=True)
        
        identity = device["identity"]
        
        # Generate spoofed properties
        props = generate_props_config(identity, device["brand"], device["model"])
        
        # Create config.ini with full device spoofing
        config_ini = avd_path / "config.ini"
        config_content = f"""
avd.ini.encoding=UTF-8
hw.cpu.arch=x86_64
hw.cpu.ncore={config.DEFAULT_CORES}
hw.ramSize={config.DEFAULT_RAM}
hw.gpu.enabled=yes
hw.gpu.mode=auto
hw.keyboard=yes
image.sysdir.1={android_info['image'].replace(';', '/')}
tag.display=Google Play
tag.id=google_apis_playstore

# Anti-detection: Device Identity
hw.device.name={identity.get('device', 'generic')}
hw.device.manufacturer={identity.get('manufacturer', 'Samsung')}
avd.name={identity.get('model', 'SM-S928B')}
avd.id={device['avd_name']}

# Hide emulator indicators
kernel.newDeviceNaming=yes
kernel.supportsGPUDirectAccess=yes
showDeviceFrame=no

# Properties for device identity
ro.product.model={identity.get('model', 'SM-S928B')}
ro.product.brand={identity.get('brand', 'samsung')}
ro.product.manufacturer={identity.get('manufacturer', 'samsung')}
ro.product.device={identity.get('device', 'e2s')}
ro.product.name={identity.get('product', 'e2sxxx')}
ro.build.fingerprint={identity.get('fingerprint', '')}
ro.serialno={identity.get('serial', '')}
ro.kernel.qemu=0
ro.boot.qemu=0
ro.hardware={identity.get('board', 'qcom')}
ro.build.characteristics=default

{props}
"""
        with open(config_ini, "w") as f:
            f.write(config_content.strip())
        
        # Create .ini pointer file
        ini_file = Path.home() / ".android" / "avd" / f"{device['avd_name']}.ini"
        with open(ini_file, "w") as f:
            f.write(f"avd.ini.encoding=UTF-8\npath={avd_path}\ntarget=android-{android_info['api']}")
    
    def launch_device(self, name, enable_frida=False):
        """Launch a device by name"""
        device = self.get_device(name)
        if not device:
            raise ValueError(f"Device not found: {name}")
        
        if self._is_running(name):
            raise ValueError(f"Device already running: {name}")
        
        # Build emulator command
        cmd = [
            config.EMULATOR_PATH,
            "-avd", device["avd_name"],
            "-no-snapshot-save",
            "-no-boot-anim",
        ]
        
        # Add proxy if configured
        if device.get("proxy"):
            proxy = device["proxy"]
            if proxy.startswith("socks5://"):
                proxy_addr = proxy.replace("socks5://", "")
                cmd.extend(["-http-proxy", f"socks5://{proxy_addr}"])
            else:
                cmd.extend(["-http-proxy", proxy])
        
        # Launch emulator
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            self._running_processes[name] = process.pid
            
            # Always apply system-level spoofing after boot
            self._apply_system_spoof(device)
            self._apply_hardware_spoof(device)
            
            # Apply Frida hooks if requested
            if enable_frida:
                self._apply_frida_hooks(device)
            
        except FileNotFoundError:
            raise RuntimeError("Android emulator not found. Check SDK installation.")
        
        return True
    
    def stop_device(self, name):
        """Stop a running device"""
        device = self.get_device(name)
        if not device:
            raise ValueError(f"Device not found: {name}")
        
        # Kill emulator via ADB
        try:
            subprocess.run(
                [config.ADB_PATH, "-s", f"emulator-5554", "emu", "kill"],
                capture_output=True,
                timeout=10
            )
        except Exception:
            pass
        
        if name in self._running_processes:
            del self._running_processes[name]
        
        return True
    
    def delete_device(self, name):
        """Delete a device"""
        device = self.get_device(name)
        if not device:
            raise ValueError(f"Device not found: {name}")
        
        # Stop if running
        if self._is_running(name):
            self.stop_device(name)
        
        # Delete AVD
        avd_path = Path.home() / ".android" / "avd" / f"{device['avd_name']}.avd"
        if avd_path.exists():
            import shutil
            shutil.rmtree(avd_path)
        
        ini_file = Path.home() / ".android" / "avd" / f"{device['avd_name']}.ini"
        if ini_file.exists():
            ini_file.unlink()
        
        # Delete device config
        device_file = self.devices_dir / f"{name}.json"
        if device_file.exists():
            device_file.unlink()
        
        return True
    
    def _is_running(self, name):
        """Check if device is running"""
        if name in self._running_processes:
            pid = self._running_processes[name]
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                del self._running_processes[name]
        return False
    
    def _apply_frida_hooks(self, device):
        """Apply Frida hooks for anti-detection"""
        from core.hook_manager import HookManager
        from spoof.battery_spoof import BatterySimulator
        from spoof.sensor_simulator import SensorSimulator
        import threading
        
        def run_hooks():
            # Wait for device to boot
            import time
            time.sleep(15)  # Wait for boot to finish mostly
            
            # Initialize hook manager
            hooks = HookManager()
            
            # Wait for device to be ready
            if not hooks.wait_for_device(timeout=60):
                print(f"[AntiDetect] Device not ready for {device['name']}")
                return
            
            # Apply all Frida hooks
            if hooks.apply_all_protections(device["identity"]):
                print(f"[AntiDetect] Frida hooks applied to {device['name']}")
            else:
                print(f"[AntiDetect] Failed to apply Frida hooks for {device['name']}")
            
            # Start battery simulation
            battery_sim = BatterySimulator()
            battery_sim.start_simulation(device.get("model", "Samsung Galaxy S24"))
            print(f"[AntiDetect] Battery simulation started for {device['name']}")
            
            # Start sensor simulation
            sensor_sim = SensorSimulator()
            sensor_sim.start_simulation(mode="idle")
            print(f"[AntiDetect] Sensor simulation started for {device['name']}")
            
            # Store simulators for cleanup
            device["_battery_sim"] = battery_sim
            device["_sensor_sim"] = sensor_sim
                
        # Run in background to not block launch
        thread = threading.Thread(target=run_hooks, daemon=True)
        thread.start()
    
    def _apply_hardware_spoof(self, device):
        """Apply hardware spoofing at boot"""
        from spoof.hardware_spoof import HardwareSpoofer
        import time
        
        def spoof():
            time.sleep(10)  # Wait for device
            spoofer = HardwareSpoofer()
            spoofer.spoof_all(device["identity"])
            print(f"[AntiDetect] Hardware spoofing applied for {device['name']}")
        
        import threading
        thread = threading.Thread(target=spoof, daemon=True)
        thread.start()
    
    def _apply_system_spoof(self, device):
        """Apply system-level spoofing via ADB"""
        from spoof.system_spoof import apply_system_spoofing_async
        
        apply_system_spoofing_async("emulator-5554", device["identity"])
        print(f"[AntiDetect] System spoofing scheduled for {device['name']}")

