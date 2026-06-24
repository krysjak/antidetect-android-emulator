"""
Frida Server Manager - Auto-download and install frida-server
"""
import os
import subprocess
import urllib.request
import lzma
import shutil
from pathlib import Path
import config


FRIDA_VERSION = "16.1.4"  # Stable version
FRIDA_SERVER_URL = f"https://github.com/frida/frida/releases/download/{FRIDA_VERSION}/frida-server-{FRIDA_VERSION}-android-x86_64.xz"
FRIDA_SERVER_PATH = Path(config.DATA_DIR) / "frida-server"


class FridaServerManager:
    """Manage frida-server installation on emulator"""
    
    def __init__(self, device_serial="emulator-5554"):
        self.device_serial = device_serial
        self.adb = config.ADB_PATH
        self.local_server_path = FRIDA_SERVER_PATH
    
    def _adb(self, command, timeout=60):
        """Execute ADB command"""
        cmd = [self.adb, "-s", self.device_serial] + command
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def is_installed(self):
        """Check if frida-server is on device"""
        success, output = self._adb(["shell", "ls", "/data/local/tmp/frida-server"])
        return success and "No such file" not in output
    
    def is_running(self):
        """Check if frida-server is running"""
        success, output = self._adb(["shell", "ps", "-A"])
        return success and "frida-server" in output
    
    def download_server(self):
        """Download frida-server from GitHub"""
        if self.local_server_path.exists():
            print(f"[Frida] Using cached server: {self.local_server_path}")
            return True
        
        print(f"[Frida] Downloading frida-server v{FRIDA_VERSION}...")
        xz_path = self.local_server_path.with_suffix(".xz")
        
        try:
            # Download
            urllib.request.urlretrieve(FRIDA_SERVER_URL, xz_path)
            print("[Frida] Download complete, extracting...")
            
            # Extract
            with lzma.open(xz_path, "rb") as f_in:
                with open(self.local_server_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Cleanup
            xz_path.unlink()
            print(f"[Frida] Server extracted to: {self.local_server_path}")
            return True
            
        except Exception as e:
            print(f"[Frida] Download failed: {e}")
            return False
    
    def push_to_device(self):
        """Push frida-server to device"""
        if not self.local_server_path.exists():
            if not self.download_server():
                return False
        
        print("[Frida] Pushing to device...")
        success, _ = self._adb(["push", str(self.local_server_path), "/data/local/tmp/frida-server"])
        
        if success:
            # Make executable
            self._adb(["shell", "chmod", "755", "/data/local/tmp/frida-server"])
            print("[Frida] Server pushed and ready")
            return True
        else:
            print("[Frida] Failed to push server")
            return False
    
    def start_server(self):
        """Start frida-server on device"""
        if not self.is_installed():
            if not self.push_to_device():
                return False
        
        if self.is_running():
            print("[Frida] Server already running")
            return True
        
        print("[Frida] Starting server...")
        # Start in background
        self._adb(["shell", "su", "-c", "/data/local/tmp/frida-server -D &"])
        
        import time
        time.sleep(2)
        
        if self.is_running():
            print("[Frida] Server started successfully!")
            return True
        else:
            # Try without su
            self._adb(["shell", "/data/local/tmp/frida-server -D &"])
            time.sleep(2)
            return self.is_running()
    
    def stop_server(self):
        """Stop frida-server"""
        self._adb(["shell", "pkill", "-f", "frida-server"])
        print("[Frida] Server stopped")
    
    def ensure_ready(self):
        """Ensure frida-server is downloaded, installed, and running"""
        if not self.local_server_path.exists():
            print("[Frida] Server not cached, downloading...")
            if not self.download_server():
                return False
        
        if not self.is_installed():
            print("[Frida] Server not on device, installing...")
            if not self.push_to_device():
                return False
        
        if not self.is_running():
            print("[Frida] Server not running, starting...")
            if not self.start_server():
                return False
        
        return True


def ensure_frida_server(device_serial="emulator-5554"):
    """Convenience function to ensure frida-server is ready"""
    manager = FridaServerManager(device_serial)
    return manager.ensure_ready()
