"""
GPU Spoofing - OpenGL ES renderer and vendor spoofing
"""
import subprocess
import config


# Real GPU data for popular devices
GPU_PROFILES = {
    "Samsung": {
        "S24": {"renderer": "Mali-G720", "vendor": "ARM", "version": "OpenGL ES 3.2 v1.r43p0"},
        "S23": {"renderer": "Adreno (TM) 740", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0738.0"},
        "S22": {"renderer": "Xclipse 920", "vendor": "Samsung", "version": "OpenGL ES 3.2 V@0635.0"},
        "A54": {"renderer": "Mali-G68", "vendor": "ARM", "version": "OpenGL ES 3.2 v1.r38p0"},
        "default": {"renderer": "Adreno (TM) 660", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0615.0"}
    },
    "Xiaomi": {
        "14": {"renderer": "Adreno (TM) 750", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0800.0"},
        "13": {"renderer": "Adreno (TM) 740", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0738.0"},
        "Note 13": {"renderer": "Mali-G610 MC6", "vendor": "ARM", "version": "OpenGL ES 3.2 v1.r38p0"},
        "default": {"renderer": "Adreno (TM) 660", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0615.0"}
    },
    "Google": {
        "Pixel 8": {"renderer": "Mali-G715", "vendor": "ARM", "version": "OpenGL ES 3.2 v1.0"},
        "Pixel 7": {"renderer": "Mali-G710", "vendor": "ARM", "version": "OpenGL ES 3.2 v1.0"},
        "Pixel 6": {"renderer": "Mali-G78", "vendor": "ARM", "version": "OpenGL ES 3.2 V@0530.0"},
        "default": {"renderer": "Mali-G710", "vendor": "ARM", "version": "OpenGL ES 3.2 v1.0"}
    },
    "OnePlus": {
        "12": {"renderer": "Adreno (TM) 750", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0800.0"},
        "11": {"renderer": "Adreno (TM) 740", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0738.0"},
        "default": {"renderer": "Adreno (TM) 660", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0615.0"}
    },
    "default": {"renderer": "Adreno (TM) 660", "vendor": "Qualcomm", "version": "OpenGL ES 3.2 V@0615.0"}
}


class GPUSpoofer:
    """Spoof OpenGL ES renderer information"""
    
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
    
    def get_gpu_profile(self, brand, model_name):
        """Get appropriate GPU profile for device"""
        brand_gpus = GPU_PROFILES.get(brand, GPU_PROFILES["default"])
        
        if isinstance(brand_gpus, dict) and "renderer" not in brand_gpus:
            # Brand has model-specific profiles
            for model_key, gpu_data in brand_gpus.items():
                if model_key != "default" and model_key.lower() in model_name.lower():
                    return gpu_data
            return brand_gpus.get("default", GPU_PROFILES["default"])
        
        return brand_gpus
    
    def generate_gpu_identity(self, brand, model_name):
        """Generate complete GPU identity for Frida injection"""
        gpu = self.get_gpu_profile(brand, model_name)
        
        return {
            "gl_renderer": gpu["renderer"],
            "gl_vendor": gpu["vendor"],
            "gl_version": gpu["version"],
            "gl_extensions": self._get_realistic_extensions(gpu["vendor"])
        }
    
    def _get_realistic_extensions(self, vendor):
        """Get realistic GL extensions for vendor"""
        common_extensions = [
            "GL_OES_EGL_image",
            "GL_OES_EGL_image_external",
            "GL_OES_depth_texture",
            "GL_OES_packed_depth_stencil",
            "GL_OES_rgb8_rgba8",
            "GL_EXT_texture_format_BGRA8888",
            "GL_OES_texture_float",
            "GL_OES_texture_half_float",
        ]
        
        if vendor == "Qualcomm":
            common_extensions.extend([
                "GL_QCOM_tiled_rendering",
                "GL_QCOM_alpha_test",
                "GL_EXT_disjoint_timer_query",
            ])
        elif vendor == "ARM":
            common_extensions.extend([
                "GL_ARM_rgba8",
                "GL_ARM_mali_shader_binary",
                "GL_ARM_mali_program_binary",
            ])
        
        return " ".join(common_extensions)
    
    def spoof_gpu_props(self, brand, model_name):
        """Apply GPU spoofing via ADB (limited effectiveness)"""
        gpu = self.get_gpu_profile(brand, model_name)
        
        # These properties may be read-only, but we try
        props = {
            "ro.hardware.egl": gpu["vendor"].lower(),
            "ro.hardware.vulkan": gpu["vendor"].lower(),
            "debug.hwui.renderer": "skiagl",  # Modern renderer
        }
        
        for key, value in props.items():
            self._adb(["shell", "setprop", key, value])
        
        return gpu


def get_gpu_for_device(brand, model_name):
    """Convenience function to get GPU data"""
    spoofer = GPUSpoofer()
    return spoofer.generate_gpu_identity(brand, model_name)
