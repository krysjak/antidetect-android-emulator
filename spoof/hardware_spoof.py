"""
Hardware ID Spoofing - IMEI, MAC, Serial Number spoofing via ADB
"""
import subprocess
import config


class HardwareSpoofer:
    """Spoof hardware identifiers on running emulator"""
    
    def __init__(self, device_serial="emulator-5554"):
        self.device_serial = device_serial
        self.adb = config.ADB_PATH
    
    def _adb(self, command):
        """Execute ADB command"""
        cmd = [self.adb, "-s", self.device_serial] + command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            print(f"ADB error: {e}")
            return None
    
    def spoof_all(self, identity):
        """Apply all hardware spoofing"""
        self.spoof_build_props(identity)
        self.spoof_imei(identity.get("imei"))
        self.spoof_serial(identity.get("serial"))
        self.spoof_android_id(identity.get("android_id"))
        self.hide_emulator_files()
    
    def spoof_build_props(self, identity):
        """Spoof build.prop values"""
        props = {
            "ro.product.model": identity.get("model", ""),
            "ro.product.brand": identity.get("brand", ""),
            "ro.product.manufacturer": identity.get("manufacturer", ""),
            "ro.product.device": identity.get("device", ""),
            "ro.product.board": identity.get("board", ""),
            "ro.build.fingerprint": identity.get("fingerprint", ""),
            "ro.serialno": identity.get("serial", ""),
            "ro.kernel.qemu": "0",
            "ro.hardware": identity.get("board", "unknown"),
        }
        
        for key, value in props.items():
            if value:
                self._adb(["shell", "setprop", key, value])
    
    def spoof_imei(self, imei):
        """Spoof IMEI (requires root)"""
        if not imei:
            return
        
        commands = [
            f"service call iphonesubinfo 1 s16 {imei}",
            f"setprop gsm.sim.operator.numeric {imei[:6]}",
        ]
        
        for cmd in commands:
            self._adb(["shell", "su", "-c", cmd])
    
    def spoof_serial(self, serial):
        """Spoof device serial number"""
        if not serial:
            return
        
        self._adb(["shell", "setprop", "ro.serialno", serial])
        self._adb(["shell", "setprop", "ro.boot.serialno", serial])
    
    def spoof_android_id(self, android_id):
        """Spoof Android ID"""
        if not android_id:
            return
        
        # Settings.Secure.ANDROID_ID
        self._adb([
            "shell", "settings", "put", "secure",
            "android_id", android_id
        ])
    
    def spoof_mac_address(self, mac_address):
        """Spoof WiFi MAC address (requires root)"""
        if not mac_address:
            return
        
        commands = [
            "ip link set wlan0 down",
            f"ip link set wlan0 address {mac_address}",
            "ip link set wlan0 up",
        ]
        
        for cmd in commands:
            self._adb(["shell", "su", "-c", cmd])
    
    def hide_emulator_files(self):
        """Hide common emulator indicator files"""
        files_to_hide = [
            "/system/bin/qemu-props",
            "/system/lib/libc_malloc_debug_qemu.so",
            "/dev/socket/qemud",
            "/dev/qemu_pipe",
        ]
        
        for file_path in files_to_hide:
            # Move/rename instead of delete
            self._adb(["shell", "su", "-c", f"mv {file_path} {file_path}.bak 2>/dev/null"])
    
    def spoof_cpu_info(self):
        """Modify /proc/cpuinfo to hide emulator (requires kernel module)"""
        # This is a placeholder - actual implementation requires kernel-level access
        # or Magisk module
        pass
    
    def get_current_props(self):
        """Get current device properties for debugging"""
        props = {}
        important_props = [
            "ro.product.model",
            "ro.product.brand",
            "ro.product.manufacturer",
            "ro.build.fingerprint",
            "ro.serialno",
            "ro.kernel.qemu",
            "ro.hardware",
        ]
        
        for prop in important_props:
            value = self._adb(["shell", "getprop", prop])
            props[prop] = value
        
        return props
    
    def spoof_bluetooth_mac(self, mac_address):
        """Spoof Bluetooth MAC address (requires root)"""
        if not mac_address:
            return
        
        # Bluetooth MAC spoofing via settings
        self._adb(["shell", "settings", "put", "secure", "bluetooth_address", mac_address])
        
        # Alternative via file system (if available)
        self._adb(["shell", "su", "-c", f"echo '{mac_address}' > /data/misc/bluetooth/.bt_nv.bin"])
    
    def spoof_baseband(self, baseband_version):
        """Spoof baseband/modem version"""
        if not baseband_version:
            return
        
        self._adb(["shell", "setprop", "gsm.version.baseband", baseband_version])
        self._adb(["shell", "setprop", "ro.baseband", baseband_version])
    
    def spoof_bootloader(self, bootloader_version):
        """Spoof bootloader version"""
        if not bootloader_version:
            return
        
        self._adb(["shell", "setprop", "ro.bootloader", bootloader_version])
    
    def spoof_all(self, identity):
        """Apply all hardware spoofing"""
        self.spoof_build_props(identity)
        self.spoof_imei(identity.get("imei"))
        self.spoof_serial(identity.get("serial"))
        self.spoof_android_id(identity.get("android_id"))
        self.spoof_mac_address(identity.get("wifi_mac"))
        self.spoof_bluetooth_mac(identity.get("bluetooth_mac"))
        self.spoof_baseband(identity.get("baseband"))
        self.spoof_bootloader(identity.get("bootloader"))
        self.hide_emulator_files()
