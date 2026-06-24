"""
AntiDetect Emulator - Web GUI Dashboard
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json

socketio = SocketIO()


def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "antidetect-secret-key"
    
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Import here to avoid circular imports
    from core.device_manager import DeviceManager
    from profiles.device_profiles import get_all_models, search_models
    import config
    
    manager = DeviceManager()
    
    @app.route("/")
    def index():
        """Main dashboard page"""
        return render_template("index.html")
    
    @app.route("/api/devices")
    def get_devices():
        """Get all devices"""
        devices = manager.list_devices()
        return jsonify(devices)
    
    @app.route("/api/devices", methods=["POST"])
    def create_device():
        """Create a new device"""
        data = request.json
        try:
            device = manager.create_device(
                model=data.get("model"),
                android_version=data.get("android_version", "14"),
                name=data.get("name"),
                proxy=data.get("proxy")
            )
            return jsonify({"success": True, "device": device})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @app.route("/api/devices/<name>/launch", methods=["POST"])
    def launch_device(name):
        """Launch a device"""
        try:
            data = request.json or {}
            manager.launch_device(name, enable_frida=data.get("frida", False))
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @app.route("/api/devices/<name>/stop", methods=["POST"])
    def stop_device(name):
        """Stop a device"""
        try:
            manager.stop_device(name)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @app.route("/api/devices/<name>", methods=["DELETE"])
    def delete_device(name):
        """Delete a device"""
        try:
            manager.delete_device(name)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
    
    @app.route("/api/models")
    def get_models():
        """Get all available phone models"""
        models = get_all_models()
        return jsonify(models)
    
    @app.route("/api/models/search")
    def search_phone_models():
        """Search phone models"""
        query = request.args.get("q", "")
        results = search_models(query)
        return jsonify(results)
    
    @app.route("/api/android-versions")
    def get_android_versions():
        """Get supported Android versions"""
        versions = []
        for ver, info in config.ANDROID_VERSIONS.items():
            versions.append({
                "version": ver,
                "api": info["api"],
                "codename": info["codename"]
            })
        return jsonify(versions)
    
    @app.route("/api/device/<name>/identity")
    def get_device_identity(name):
        """Get device identity details"""
        device = manager.get_device(name)
        if device:
            return jsonify(device.get("identity", {}))
        return jsonify({"error": "Device not found"}), 404
    
    # =========================================
    # ANTIDETECT API ENDPOINTS
    # =========================================
    
    @app.route("/api/status/adb")
    def get_adb_status():
        """Get ADB connection status"""
        import subprocess
        try:
            result = subprocess.run(
                [config.ADB_PATH, "devices", "-l"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            devices = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            "serial": parts[0],
                            "status": parts[1]
                        })
            return jsonify({
                "connected": len(devices) > 0,
                "devices": devices
            })
        except Exception as e:
            return jsonify({"connected": False, "error": str(e)})
    
    @app.route("/api/status/frida")
    def get_frida_status():
        """Get Frida server status"""
        from frida.frida_server_manager import FridaServerManager, FRIDA_SERVER_PATH
        
        fm = FridaServerManager()
        return jsonify({
            "downloaded": FRIDA_SERVER_PATH.exists(),
            "installed": fm.is_installed(),
            "running": fm.is_running(),
            "version": "16.1.4"
        })
    
    @app.route("/api/frida/install", methods=["POST"])
    def install_frida():
        """Download and install Frida server"""
        from frida.frida_server_manager import FridaServerManager
        
        fm = FridaServerManager()
        
        # Download if needed
        if not fm.local_server_path.exists():
            if not fm.download_server():
                return jsonify({"success": False, "error": "Download failed"})
        
        # Push to device
        if not fm.push_to_device():
            return jsonify({"success": False, "error": "Push to device failed"})
        
        # Start server
        if not fm.start_server():
            return jsonify({"success": False, "error": "Start server failed"})
        
        return jsonify({"success": True})
    
    @app.route("/api/devices/<name>/apply-antidetect", methods=["POST"])
    def apply_antidetect(name):
        """Apply antidetect spoofing to running device"""
        device = manager.get_device(name)
        if not device:
            return jsonify({"success": False, "error": "Device not found"})
        
        identity = device.get("identity", {})
        
        # Apply system spoof
        from spoof.system_spoof import SystemSpoofer
        spoofer = SystemSpoofer()
        
        # Check if device is ready
        if not spoofer.wait_for_boot(timeout=10):
            return jsonify({"success": False, "error": "Device not ready (check ADB)"})
        
        spoofer.apply_all_spoofing(identity)
        
        # Apply hardware spoof
        from spoof.hardware_spoof import HardwareSpoofer
        hw = HardwareSpoofer()
        hw.spoof_all(identity)
        
        return jsonify({
            "success": True, 
            "message": "Antidetect applied! Restart Settings app to see changes."
        })
    
    @app.route("/api/devices/<name>/apply-frida-hooks", methods=["POST"])
    def apply_frida_hooks(name):
        """Apply Frida hooks to running device"""
        device = manager.get_device(name)
        if not device:
            return jsonify({"success": False, "error": "Device not found"})
        
        from core.hook_manager import HookManager
        hm = HookManager()
        
        if not hm.start_frida_server():
            return jsonify({"success": False, "error": "Could not start Frida server"})
        
        identity = device.get("identity", {})
        success = hm.inject_hooks("com.android.settings", identity)
        
        return jsonify({
            "success": success,
            "message": "Frida hooks applied to Settings" if success else "Failed to apply hooks"
        })
    
    @socketio.on("connect")
    def handle_connect():
        """Handle client connection"""
        emit("connected", {"status": "ok"})
    
    @socketio.on("refresh_devices")
    def handle_refresh():
        """Refresh device list"""
        devices = manager.list_devices()
        emit("devices_updated", devices)
    
    return app
