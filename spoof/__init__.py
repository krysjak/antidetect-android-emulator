"""Spoof Module - Hardware and software identity spoofing"""
from .hardware_spoof import HardwareSpoofer
from .sensor_simulator import SensorSimulator
from .gpu_spoof import GPUSpoofer, get_gpu_for_device
from .battery_spoof import BatterySimulator, generate_battery_identity

__all__ = [
    "HardwareSpoofer",
    "SensorSimulator",
    "GPUSpoofer",
    "get_gpu_for_device",
    "BatterySimulator",
    "generate_battery_identity"
]
