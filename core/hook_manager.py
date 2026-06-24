"""
Hook Manager - Centralized Frida hook management
"""
import os
import subprocess
import time
import threading
from pathlib import Path
from typing import Optional, Dict, List

import config


class HookManager:
    """Centralized management for all Frida anti-detection hooks"""
    
    def __init__(self, device_serial: str = "emulator-5554"):
        self.device_serial = device_serial
        self.adb = config.ADB_PATH
        self.scripts_dir = Path(__file__).parent.parent / "frida" / "scripts"
        self._active_sessions = {}
        self._frida_server_started = False
    
    def _adb(self, command: List[str]) -> Optional[str]:
        """Execute ADB command"""
        cmd = [self.adb, "-s", self.device_serial] + command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            print(f"[HookManager] ADB error: {e}")
            return None
    
    def is_device_ready(self) -> bool:
        """Check if device is booted and ready"""
        result = self._adb(["shell", "getprop", "sys.boot_completed"])
        return result == "1"
    
    def wait_for_device(self, timeout: int = 120) -> bool:
        """Wait for device to be ready"""
        start = time.time()
        while time.time() - start < timeout:
            if self.is_device_ready():
                return True
            time.sleep(2)
        return False
    
    def is_frida_server_running(self) -> bool:
        """Check if Frida server is running on device"""
        output = self._adb(["shell", "ps", "-A"])
        if output:
            return "frida-server" in output
        return False
    
    def start_frida_server(self) -> bool:
        """Start Frida server on device"""
        if self._frida_server_started and self.is_frida_server_running():
            return True
        
        # Check if frida-server exists
        exists = self._adb(["shell", "ls", "/data/local/tmp/frida-server"])
        if not exists or "No such file" in exists:
            print("[HookManager] Frida server not found. Attempting to push...")
            if not self._push_frida_server():
                print("[HookManager] Please push frida-server manually to /data/local/tmp/")
                return False
        
        # Make executable
        self._adb(["shell", "chmod", "755", "/data/local/tmp/frida-server"])
        
        # Start in background
        self._adb(["shell", "su", "-c", "/data/local/tmp/frida-server -D &"])
        time.sleep(2)
        
        self._frida_server_started = self.is_frida_server_running()
        return self._frida_server_started
    
    def _push_frida_server(self) -> bool:
        """Push frida-server binary to device (downloads if needed)"""
        try:
            from frida.frida_server_manager import FridaServerManager
            manager = FridaServerManager(self.device_serial)
            return manager.push_to_device()
        except Exception as e:
            print(f"[HookManager] Frida server manager error: {e}")
            
            # Fallback to manual check
            possible_paths = [
                Path(config.DATA_DIR) / "frida-server",
                Path.home() / "frida-server",
                Path(__file__).parent.parent / "bin" / "frida-server",
            ]
            
            for path in possible_paths:
                if path.exists():
                    result = subprocess.run(
                        [self.adb, "-s", self.device_serial, "push", str(path), "/data/local/tmp/frida-server"],
                        capture_output=True
                    )
                    return result.returncode == 0
            
            return False
    
    def generate_combined_script(self, identity: Dict) -> str:
        """Generate a combined Frida script with all hooks and identity values"""
        combined = "// Combined AntiDetect Frida Script\n\n"
        
        # Add config object
        combined += self._generate_config_js(identity)
        combined += "\n\n"
        
        # Load all scripts in order
        script_files = [
            "native_hooks.js",
            "safetynet_bypass.js",
            "anti_detect.js",
        ]
        
        for script_name in script_files:
            script_path = self.scripts_dir / script_name
            if script_path.exists():
                with open(script_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Replace placeholders with actual values
                    content = self._replace_placeholders(content, identity)
                    combined += f"// ========== {script_name} ==========\n"
                    combined += content
                    combined += "\n\n"
        
        return combined
    
    def _generate_config_js(self, identity: Dict) -> str:
        """Generate JavaScript config object from identity"""
        return f"""
// Device identity configuration
var deviceIdentity = {{
    imei: "{identity.get('imei', '')}",
    serial: "{identity.get('serial', '')}",
    androidId: "{identity.get('android_id', '')}",
    model: "{identity.get('model', '')}",
    brand: "{identity.get('brand', '')}",
    manufacturer: "{identity.get('manufacturer', '')}",
    fingerprint: "{identity.get('fingerprint', '')}",
    device: "{identity.get('device', '')}",
    board: "{identity.get('board', '')}",
    product: "{identity.get('product', '')}",
    hardware: "{identity.get('board', '')}",
    bootloader: "{identity.get('bootloader', 'unknown')}",
    baseband: "{identity.get('baseband', 'unknown')}",
    wifiMac: "{identity.get('wifi_mac', '')}",
    bluetoothMac: "{identity.get('bluetooth_mac', '')}",
    glRenderer: "{identity.get('gl_renderer', 'Adreno (TM) 660')}",
    glVendor: "{identity.get('gl_vendor', 'Qualcomm')}"
}};

// Alias for compatibility
var config = deviceIdentity;
"""
    
    def _replace_placeholders(self, content: str, identity: Dict) -> str:
        """Replace {{PLACEHOLDER}} values in script content"""
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
            "{{PRODUCT}}": identity.get("product", identity.get("device", "")),
            "{{HARDWARE}}": identity.get("board", ""),
            "{{BOOTLOADER}}": identity.get("bootloader", "unknown"),
            "{{BASEBAND}}": identity.get("baseband", "unknown"),
            "{{CPU_MODEL}}": identity.get("cpu_model", "Qualcomm Kryo 585"),
            "{{CPU_HARDWARE}}": identity.get("cpu_hardware", "qcom"),
            "{{CPU_FEATURES}}": identity.get("cpu_features", ""),
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))
        
        return content
    
    def inject_hooks(self, package_name: str, identity: Dict) -> bool:
        """Inject all anti-detection hooks into target app"""
        if not self.start_frida_server():
            print("[HookManager] Failed to start Frida server")
            return False
        
        # Generate combined script
        script_content = self.generate_combined_script(identity)
        
        # Write to temp file
        temp_script = Path(config.DATA_DIR) / "combined_hooks.js"
        with open(temp_script, "w", encoding="utf-8") as f:
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
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._active_sessions[package_name] = process.pid
            print(f"[HookManager] Hooks injected into {package_name}")
            return True
        except FileNotFoundError:
            print("[HookManager] Frida not found. Install with: pip install frida-tools")
            return False
        except Exception as e:
            print(f"[HookManager] Injection error: {e}")
            return False
    
    def inject_system_wide(self, identity: Dict) -> bool:
        """Inject hooks into system apps (Settings, etc.)"""
        system_apps = [
            "com.android.settings",
            "com.google.android.gms",  # Google Play Services
        ]
        
        for app in system_apps:
            self.inject_hooks(app, identity)
            time.sleep(1)
        
        return True
    
    def spawn_with_hooks(self, package_name: str, identity: Dict) -> bool:
        """Spawn app with Frida hooks attached from start"""
        return self.inject_hooks(package_name, identity)
    
    def stop_session(self, package_name: str):
        """Stop active Frida session"""
        if package_name in self._active_sessions:
            pid = self._active_sessions[package_name]
            try:
                os.kill(pid, 9)
            except Exception:
                pass
            del self._active_sessions[package_name]
    
    def stop_all_sessions(self):
        """Stop all active Frida sessions"""
        for package in list(self._active_sessions.keys()):
            self.stop_session(package)
    
    def get_available_scripts(self) -> List[str]:
        """Get list of available Frida scripts"""
        scripts = []
        if self.scripts_dir.exists():
            for script in self.scripts_dir.glob("*.js"):
                scripts.append(script.name)
        return scripts
    
    def apply_all_protections(self, identity: Dict) -> bool:
        """Apply all anti-detection protections"""
        print("[HookManager] Applying all anti-detection protections...")
        
        # Wait for device
        if not self.wait_for_device(timeout=60):
            print("[HookManager] Device not ready")
            return False
        
        # Start Frida server
        if not self.start_frida_server():
            print("[HookManager] Could not start Frida server")
            return False
        
        # Inject into system apps
        self.inject_system_wide(identity)
        
        print("[HookManager] All protections applied!")
        return True


def apply_antidetect_hooks(device_serial: str, identity: Dict, async_mode: bool = True):
    """Convenience function to apply all antidetect hooks"""
    manager = HookManager(device_serial)
    
    if async_mode:
        thread = threading.Thread(
            target=manager.apply_all_protections,
            args=(identity,),
            daemon=True
        )
        thread.start()
        return thread
    else:
        return manager.apply_all_protections(identity)
