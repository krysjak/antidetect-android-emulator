"""
Core Module - Device management and hook orchestration
"""
from .device_manager import DeviceManager
from .hook_manager import HookManager, apply_antidetect_hooks

__all__ = [
    "DeviceManager",
    "HookManager",
    "apply_antidetect_hooks"
]
