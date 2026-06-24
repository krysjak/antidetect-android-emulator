"""
Battery Spoofing - Realistic battery state simulation
"""
import subprocess
import random
import threading
import time
import math
import config


# Battery profiles for different device types
BATTERY_PROFILES = {
    "flagship": {
        "capacity_mah": 5000,
        "voltage_mv": 4350,
        "technology": "Li-poly",
        "health": "Good",
        "discharge_rate": 0.15,  # % per minute under normal use
        "temperature_base": 28.0,
        "temperature_variance": 5.0
    },
    "midrange": {
        "capacity_mah": 4500,
        "voltage_mv": 4200,
        "technology": "Li-ion",
        "health": "Good",
        "discharge_rate": 0.18,
        "temperature_base": 30.0,
        "temperature_variance": 4.0
    },
    "budget": {
        "capacity_mah": 4000,
        "voltage_mv": 4100,
        "technology": "Li-ion",
        "health": "Good",
        "discharge_rate": 0.20,
        "temperature_base": 32.0,
        "temperature_variance": 3.0
    }
}

# Device tier mapping
DEVICE_TIERS = {
    "Samsung Galaxy S24": "flagship",
    "Samsung Galaxy S23": "flagship",
    "Samsung Galaxy S22": "flagship",
    "Samsung Galaxy A54": "midrange",
    "Samsung Galaxy A34": "midrange",
    "Xiaomi 14": "flagship",
    "Xiaomi 13": "flagship",
    "Redmi Note 13": "midrange",
    "Google Pixel 8": "flagship",
    "Google Pixel 7": "flagship",
    "OnePlus 12": "flagship",
    "OnePlus 11": "flagship",
}


class BatterySimulator:
    """Simulate realistic battery behavior to bypass emulator detection"""
    
    def __init__(self, device_serial="emulator-5554"):
        self.device_serial = device_serial
        self.adb = config.ADB_PATH
        self._running = False
        self._thread = None
        self._current_level = random.randint(45, 85)  # Start with realistic level
        self._is_charging = False
        self._last_activity = time.time()
    
    def _adb(self, command):
        """Execute ADB command"""
        cmd = [self.adb, "-s", self.device_serial] + command
        try:
            subprocess.run(cmd, capture_output=True, timeout=5)
        except Exception:
            pass
    
    def _send_to_emulator(self, cmd):
        """Send command to emulator console"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                # Extract port from device serial (emulator-5554 -> 5554)
                port = int(self.device_serial.split("-")[1]) if "-" in self.device_serial else 5554
                s.connect(("localhost", port))
                s.recv(1024)  # Welcome message
                s.send(f"{cmd}\n".encode())
                s.recv(1024)  # Response
        except Exception:
            pass
    
    def get_battery_profile(self, model_name):
        """Get battery profile for device model"""
        for device, tier in DEVICE_TIERS.items():
            if device.lower() in model_name.lower():
                return BATTERY_PROFILES[tier]
        return BATTERY_PROFILES["flagship"]  # Default to flagship
    
    def start_simulation(self, model_name="Samsung Galaxy S24"):
        """Start continuous battery simulation"""
        if self._running:
            return
        
        self._running = True
        self._profile = self.get_battery_profile(model_name)
        self._thread = threading.Thread(
            target=self._simulate_loop,
            args=(self._profile,),
            daemon=True
        )
        self._thread.start()
        print(f"[Battery] Started simulation for {model_name}")
    
    def stop_simulation(self):
        """Stop battery simulation"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
    
    def _simulate_loop(self, profile):
        """Main simulation loop"""
        update_interval = 60  # Update every minute
        
        while self._running:
            # Calculate battery drain/charge
            if self._is_charging:
                # Charging: gain ~0.5% per minute
                self._current_level = min(100, self._current_level + 0.5)
            else:
                # Discharging: lose based on profile
                drain = profile["discharge_rate"]
                # Add some randomness
                drain *= random.uniform(0.8, 1.2)
                self._current_level = max(5, self._current_level - drain)
            
            # Calculate realistic temperature
            temp = self._calculate_temperature(profile)
            
            # Calculate voltage based on level
            voltage = self._calculate_voltage(profile)
            
            # Apply to emulator
            self._apply_battery_state(
                level=int(self._current_level),
                temperature=temp,
                voltage=voltage,
                profile=profile
            )
            
            time.sleep(update_interval)
    
    def _calculate_temperature(self, profile):
        """Calculate realistic battery temperature"""
        base = profile["temperature_base"]
        variance = profile["temperature_variance"]
        
        # Higher temp when charging
        if self._is_charging:
            base += 5
        
        # Time-based variation (warmer during day)
        hour = time.localtime().tm_hour
        if 10 <= hour <= 18:
            base += 2
        
        # Add random variance
        temp = base + random.uniform(-variance, variance)
        
        return round(temp, 1)
    
    def _calculate_voltage(self, profile):
        """Calculate voltage based on battery level"""
        max_voltage = profile["voltage_mv"]
        min_voltage = 3400  # Typical minimum
        
        # Voltage curve (not linear)
        level_factor = self._current_level / 100.0
        voltage_range = max_voltage - min_voltage
        
        # Simulate discharge curve
        voltage = min_voltage + (voltage_range * math.pow(level_factor, 0.8))
        
        return int(voltage)
    
    def _apply_battery_state(self, level, temperature, voltage, profile):
        """Apply battery state to emulator"""
        # Use emulator console
        self._send_to_emulator(f"power capacity {level}")
        
        # Status: "charging", "discharging", "not-charging", "full"
        if self._is_charging:
            if level >= 100:
                self._send_to_emulator("power status full")
            else:
                self._send_to_emulator("power status charging")
        else:
            self._send_to_emulator("power status discharging")
        
        # AC power
        if self._is_charging:
            self._send_to_emulator("power ac on")
        else:
            self._send_to_emulator("power ac off")
    
    def set_charging(self, is_charging):
        """Set charging state"""
        self._is_charging = is_charging
    
    def set_level(self, level):
        """Set battery level"""
        self._current_level = max(0, min(100, level))
    
    def get_current_state(self):
        """Get current battery state"""
        return {
            "level": int(self._current_level),
            "charging": self._is_charging,
            "health": "Good",
            "technology": self._profile["technology"] if hasattr(self, '_profile') else "Li-ion"
        }


def generate_battery_identity(model_name):
    """Generate battery identity for device profile"""
    simulator = BatterySimulator()
    profile = simulator.get_battery_profile(model_name)
    
    return {
        "capacity_mah": profile["capacity_mah"],
        "voltage_mv": profile["voltage_mv"],
        "technology": profile["technology"],
        "health": profile["health"],
        "current_level": random.randint(40, 90),
        "is_charging": False,
        "temperature": round(profile["temperature_base"] + random.uniform(-2, 2), 1)
    }
