"""
Update existing devices with latest anti-detection properties
"""
import json
import os
from pathlib import Path
import config
from spoof.system_props import generate_props_config

def update_all_devices():
    devices_dir = config.SAVED_DEVICES_DIR
    for device_file in devices_dir.glob("*.json"):
        with open(device_file, "r") as f:
            device = json.load(f)
        
        print(f"Updating {device['name']}...")
        
        # Re-generate props
        props = generate_props_config(device["identity"], device["brand"], device["model"])
        
        # Update config.ini
        avd_path = Path.home() / ".android" / "avd" / f"{device['avd_name']}.avd"
        config_ini = avd_path / "config.ini"
        
        if config_ini.exists():
            with open(config_ini, "r") as f:
                lines = f.readlines()
            
            # Keep hardware lines, replace spoofed lines
            new_lines = []
            spoof_keys = ["ro.product", "ro.build", "ro.kernel", "ro.hardware", "ro.boot", "gsm.", "ro.serialno", "ro.config.device_name"]
            
            for line in lines:
                if not any(line.startswith(key) for key in spoof_keys):
                    new_lines.append(line)
            
            # Add new spoofed props
            new_lines.append(props + "\n")
            
            with open(config_ini, "w") as f:
                f.writelines(new_lines)
            print(f"  ✓ config.ini updated at {config_ini}")
        else:
            print(f"  ✗ config.ini not found at {config_ini}")

if __name__ == "__main__":
    update_all_devices()
