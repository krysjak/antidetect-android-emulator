"""
Frida Hooks - Runtime anti-detection bypass
"""
import os
import subprocess
import time
from pathlib import Path

import config


class FridaHooks:
    """Inject Frida scripts for runtime anti-detection"""
    
    def __init__(self, device_serial="emulator-5554"):
        self.device_serial = device_serial
        self.adb = config.ADB_PATH
        self.scripts_dir = Path(__file__).parent / "scripts"
    
    def _adb(self, command):
        """Execute ADB command"""
        cmd = [self.adb, "-s", self.device_serial] + command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            print(f"ADB error: {e}")
            return None
    
    def is_frida_server_running(self):
        """Check if Frida server is running on device"""
        output = self._adb(["shell", "ps", "-A"])
        if output:
            return "frida-server" in output
        return False
    
    def start_frida_server(self):
        """Start Frida server on device"""
        # Check if frida-server exists
        exists = self._adb(["shell", "ls", "/data/local/tmp/frida-server"])
        if not exists or "No such file" in exists:
            print("Frida server not found on device. Please push it first.")
            return False
        
        # Start in background
        self._adb(["shell", "su", "-c", "/data/local/tmp/frida-server &"])
        time.sleep(1)
        
        return self.is_frida_server_running()
    
    def inject_anti_detect(self, package_name, identity=None):
        """Inject anti-detection script into target app"""
        script_path = self.scripts_dir / "anti_detect.js"
        
        if not script_path.exists():
            print(f"Script not found: {script_path}")
            return False
        
        # Read and customize script with device identity
        with open(script_path, "r") as f:
            script_content = f.read()
        
        if identity:
            # Replace placeholders with actual values
            replacements = {
                "{{IMEI}}": identity.get("imei", ""),
                "{{SERIAL}}": identity.get("serial", ""),
                "{{ANDROID_ID}}": identity.get("android_id", ""),
                "{{MODEL}}": identity.get("model", ""),
                "{{BRAND}}": identity.get("brand", ""),
                "{{MANUFACTURER}}": identity.get("manufacturer", ""),
                "{{FINGERPRINT}}": identity.get("fingerprint", ""),
                "{{DEVICE}}": identity.get("device", ""),
                "{{BOARD}}": identity.get("board", ""),
            }
            
            for placeholder, value in replacements.items():
                script_content = script_content.replace(placeholder, str(value))
        
        # Write temporary customized script
        temp_script = Path(config.DATA_DIR) / "temp_hook.js"
        with open(temp_script, "w") as f:
            f.write(script_content)
        
        # Run Frida
        try:
            cmd = [
                "frida",
                "-U",  # USB device
                "-l", str(temp_script),
                "-f", package_name,
                "--no-pause"
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            print("Frida not found. Install with: pip install frida-tools")
            return False
        except Exception as e:
            print(f"Frida injection error: {e}")
            return False
    
    def spawn_with_hooks(self, package_name, identity=None):
        """Spawn app with Frida hooks attached"""
        if not self.is_frida_server_running():
            if not self.start_frida_server():
                return False
        
        return self.inject_anti_detect(package_name, identity)
    
    def get_running_apps(self):
        """Get list of running apps on device"""
        try:
            import frida
            device = frida.get_usb_device()
            return device.enumerate_applications()
        except Exception as e:
            print(f"Failed to get apps: {e}")
            return []


def create_anti_detect_script(identity):
    """Generate custom anti-detection Frida script"""
    script = f"""
// Auto-generated AntiDetect Frida Script
// Identity: {identity.get('model', 'Unknown')}

var spoofedValues = {{
    imei: "{identity.get('imei', '')}",
    serial: "{identity.get('serial', '')}",
    androidId: "{identity.get('android_id', '')}",
    model: "{identity.get('model', '')}",
    brand: "{identity.get('brand', '')}",
    manufacturer: "{identity.get('manufacturer', '')}",
    fingerprint: "{identity.get('fingerprint', '')}",
    device: "{identity.get('device', '')}",
    board: "{identity.get('board', '')}"
}};

// Hook Build class
Java.perform(function() {{
    var Build = Java.use("android.os.Build");
    
    Build.MODEL.value = spoofedValues.model;
    Build.BRAND.value = spoofedValues.brand;
    Build.MANUFACTURER.value = spoofedValues.manufacturer;
    Build.FINGERPRINT.value = spoofedValues.fingerprint;
    Build.DEVICE.value = spoofedValues.device;
    Build.BOARD.value = spoofedValues.board;
    Build.HARDWARE.value = spoofedValues.board;
    Build.PRODUCT.value = spoofedValues.device;
    
    console.log("[+] Build properties spoofed");
    
    // Hook TelephonyManager for IMEI
    var TelephonyManager = Java.use("android.telephony.TelephonyManager");
    
    TelephonyManager.getDeviceId.overload().implementation = function() {{
        console.log("[+] getDeviceId hooked -> " + spoofedValues.imei);
        return spoofedValues.imei;
    }};
    
    TelephonyManager.getImei.overload().implementation = function() {{
        console.log("[+] getImei hooked -> " + spoofedValues.imei);
        return spoofedValues.imei;
    }};
    
    // Hook Settings.Secure for Android ID
    var Secure = Java.use("android.provider.Settings$Secure");
    
    Secure.getString.implementation = function(resolver, name) {{
        if (name === "android_id") {{
            console.log("[+] android_id hooked -> " + spoofedValues.androidId);
            return spoofedValues.androidId;
        }}
        return this.getString(resolver, name);
    }};
    
    console.log("[+] AntiDetect hooks installed successfully");
}});
"""
    return script
