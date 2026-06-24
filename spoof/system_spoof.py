"""
System Spoofer - Apply system-level identity changes via ADB
This runs after the emulator boots to change properties that can't be set in config.ini
"""
import subprocess
import time
import threading
import config


class SystemSpoofer:
    """Apply system-level spoofing after boot"""
    
    def __init__(self, device_serial="emulator-5554"):
        self.device_serial = device_serial
        self.adb = config.ADB_PATH
    
    def _adb(self, command, timeout=30):
        """Execute ADB command"""
        cmd = [self.adb, "-s", self.device_serial] + command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip()
        except Exception as e:
            return None
    
    def _adb_root(self):
        """Get root access"""
        self._adb(["root"])
        time.sleep(1)
        self._adb(["remount"])
        time.sleep(1)
    
    def wait_for_boot(self, timeout=120):
        """Wait for device to fully boot"""
        start = time.time()
        while time.time() - start < timeout:
            result = self._adb(["shell", "getprop", "sys.boot_completed"])
            if result == "1":
                return True
            time.sleep(2)
        return False
    
    def apply_all_spoofing(self, identity):
        """Apply all system-level spoofing"""
        print("[SystemSpoof] Waiting for device boot...")
        if not self.wait_for_boot():
            print("[SystemSpoof] Device boot timeout")
            return False
        
        print("[SystemSpoof] Applying system-level identity...")
        
        # Get root
        self._adb_root()
        
        # Apply properties
        self._apply_build_props(identity)
        self._apply_settings(identity)
        self._hide_emulator_strings()
        
        print("[SystemSpoof] System-level spoofing complete!")
        return True
    
    def _apply_build_props(self, identity):
        """Apply build properties via setprop"""
        props = {
            # Core identity
            "ro.product.model": identity.get("model", "SM-S928B"),
            "ro.product.brand": identity.get("brand", "samsung"),
            "ro.product.manufacturer": identity.get("manufacturer", "samsung"),
            "ro.product.device": identity.get("device", "e2s"),
            "ro.product.name": identity.get("product", identity.get("device", "e2s")),
            "ro.build.fingerprint": identity.get("fingerprint", ""),
            "ro.serialno": identity.get("serial", ""),
            "ro.boot.serialno": identity.get("serial", ""),
            
            # Hide emulator
            "ro.kernel.qemu": "0",
            "ro.boot.qemu": "0",
            "ro.hardware": identity.get("board", "qcom"),
            "ro.hardware.egl": "adreno",
            "ro.build.characteristics": "default",
            "ro.build.type": "user",
            "ro.build.tags": "release-keys",
            
            # GPU identity
            "ro.hardware.vulkan": identity.get("gl_vendor", "qualcomm").lower(),
            
            # Baseband
            "gsm.version.baseband": identity.get("baseband", "unknown"),
            "ro.baseband": identity.get("baseband", "unknown"),
            
            # Bootloader
            "ro.bootloader": identity.get("bootloader", "unknown"),
            
            # Hide QEMU indicators
            "init.svc.qemu-props": "",
            "qemu.hw.mainkeys": "",
            "qemu.sf.lcd_density": "",
            
            # Partition-specific (for newer Android)
            "ro.product.system.model": identity.get("model", "SM-S928B"),
            "ro.product.system.brand": identity.get("brand", "samsung"),
            "ro.product.system.manufacturer": identity.get("manufacturer", "samsung"),
            "ro.product.system.device": identity.get("device", "e2s"),
            "ro.product.vendor.model": identity.get("model", "SM-S928B"),
            "ro.product.vendor.brand": identity.get("brand", "samsung"),
            "ro.product.vendor.device": identity.get("device", "e2s"),
        }
        
        for key, value in props.items():
            if value:
                self._adb(["shell", "setprop", key, value])
        
        print(f"[SystemSpoof] Applied {len(props)} properties")
    
    def _apply_settings(self, identity):
        """Apply settings database changes"""
        # Device name in Settings
        device_name = identity.get("model", "Galaxy S24 Ultra")
        
        self._adb(["shell", "settings", "put", "global", "device_name", device_name])
        self._adb(["shell", "settings", "put", "secure", "bluetooth_name", device_name])
        self._adb(["shell", "settings", "put", "system", "device_name", device_name])
        
        # Android ID
        android_id = identity.get("android_id", "")
        if android_id:
            self._adb(["shell", "settings", "put", "secure", "android_id", android_id])
        
        print("[SystemSpoof] Settings applied")
    
    def _hide_emulator_strings(self):
        """Try to hide emulator-specific strings in system"""
        # These require system partition to be writable
        commands = [
            # Try to modify Settings strings (usually read-only)
            'settings put global emulator_device_name ""',
            
            # Disable developer settings indicators
            "settings put global development_settings_enabled 0",
            "settings put global adb_enabled 0",
        ]
        
        for cmd in commands:
            self._adb(["shell"] + cmd.split())


def apply_system_spoofing_async(device_serial, identity):
    """Apply system spoofing in background thread"""
    spoofer = SystemSpoofer(device_serial)
    
    def run():
        time.sleep(5)  # Initial delay
        spoofer.apply_all_spoofing(identity)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
