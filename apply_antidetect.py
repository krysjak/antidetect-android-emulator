"""
Apply Antidetect to Running Emulator
Run this script to apply spoofing to an already running emulator
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spoof.system_spoof import SystemSpoofer
from spoof.hardware_spoof import HardwareSpoofer
from profiles.device_profiles import get_model_profile
from profiles.profile_generator import generate_device_identity


def apply_antidetect(device_serial="emulator-5554", model_name="Samsung Galaxy S24 Ultra"):
    """Apply antidetect spoofing to running emulator"""
    
    print(f"🔧 Applying antidetect to {device_serial}")
    print(f"📱 Model: {model_name}")
    print()
    
    # Get device profile
    profile = get_model_profile(model_name)
    if not profile:
        print(f"❌ Unknown model: {model_name}")
        return False
    
    # Generate identity
    identity = generate_device_identity(profile)
    
    print(f"Generated identity:")
    print(f"  Model: {identity['model']}")
    print(f"  IMEI: {identity['imei']}")
    print(f"  Serial: {identity['serial']}")
    print(f"  GPU: {identity['gl_renderer']}")
    print()
    
    # Apply system spoof
    print("📝 Applying system properties...")
    system_spoofer = SystemSpoofer(device_serial)
    system_spoofer.apply_all_spoofing(identity)
    
    # Apply hardware spoof
    print("🔌 Applying hardware spoofing...")
    hardware_spoofer = HardwareSpoofer(device_serial)
    hardware_spoofer.spoof_all(identity)
    
    print()
    print("✅ Antidetect applied! Restart Settings app to see changes.")
    print()
    print("💡 For full protection, also run with --frida flag to inject runtime hooks")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Apply antidetect to running emulator")
    parser.add_argument("--serial", "-s", default="emulator-5554", help="Device serial")
    parser.add_argument("--model", "-m", default="Samsung Galaxy S24 Ultra", help="Phone model to emulate")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    if args.list_models:
        from profiles.device_profiles import get_all_models
        models = get_all_models()
        print("Available models:")
        for brand, devices in models.items():
            print(f"\n{brand}:")
            for d in devices:
                print(f"  - {d['name']}")
        sys.exit(0)
    
    apply_antidetect(args.serial, args.model)
