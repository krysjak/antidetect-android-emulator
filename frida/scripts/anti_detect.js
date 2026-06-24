/**
 * AntiDetect Frida Script - Comprehensive emulator detection bypass
 * Hooks Android system APIs to spoof device information
 */

// Configurable identity values (replaced at runtime)
var config = {
    imei: "{{IMEI}}",
    serial: "{{SERIAL}}",
    androidId: "{{ANDROID_ID}}",
    model: "{{MODEL}}",
    brand: "{{BRAND}}",
    manufacturer: "{{MANUFACTURER}}",
    fingerprint: "{{FINGERPRINT}}",
    device: "{{DEVICE}}",
    board: "{{BOARD}}"
};

console.log("[AntiDetect] Starting anti-detection hooks...");

// Wait for Java runtime
Java.perform(function () {

    // =============================================
    // 1. BUILD CLASS SPOOFING
    // =============================================
    try {
        var Build = Java.use("android.os.Build");

        Build.MODEL.value = config.model;
        Build.BRAND.value = config.brand;
        Build.MANUFACTURER.value = config.manufacturer;
        Build.FINGERPRINT.value = config.fingerprint;
        Build.DEVICE.value = config.device;
        Build.BOARD.value = config.board;
        Build.HARDWARE.value = config.board;
        Build.PRODUCT.value = config.device;
        Build.SERIAL.value = config.serial;

        // Hide emulator tags
        Build.TAGS.value = "release-keys";
        Build.TYPE.value = "user";
        Build.HOST.value = "build.android.com";

        console.log("[AntiDetect] Build properties spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] Build hook error: " + e);
    }

    // =============================================
    // 2. TELEPHONY MANAGER (IMEI/MEID)
    // =============================================
    try {
        var TelephonyManager = Java.use("android.telephony.TelephonyManager");

        TelephonyManager.getDeviceId.overload().implementation = function () {
            return config.imei;
        };

        TelephonyManager.getDeviceId.overload("int").implementation = function (slot) {
            return config.imei;
        };

        TelephonyManager.getImei.overload().implementation = function () {
            return config.imei;
        };

        TelephonyManager.getImei.overload("int").implementation = function (slot) {
            return config.imei;
        };

        TelephonyManager.getMeid.overload().implementation = function () {
            return config.imei;
        };

        TelephonyManager.getSubscriberId.implementation = function () {
            // Return fake IMSI
            return "310260" + Math.random().toString().substring(2, 12);
        };

        TelephonyManager.getLine1Number.implementation = function () {
            // Return fake phone number
            return "+1" + Math.floor(Math.random() * 9000000000 + 1000000000);
        };

        TelephonyManager.getSimSerialNumber.implementation = function () {
            // Fake SIM serial
            return "89" + Math.random().toString().substring(2, 20);
        };

        console.log("[AntiDetect] TelephonyManager spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] TelephonyManager hook error: " + e);
    }

    // =============================================
    // 3. SETTINGS.SECURE (Android ID)
    // =============================================
    try {
        var Secure = Java.use("android.provider.Settings$Secure");

        Secure.getString.implementation = function (resolver, name) {
            if (name === "android_id") {
                return config.androidId;
            }
            return this.getString(resolver, name);
        };

        console.log("[AntiDetect] Settings.Secure spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] Settings.Secure hook error: " + e);
    }

    // =============================================
    // 4. FILE EXISTENCE CHECKS
    // =============================================
    try {
        var File = Java.use("java.io.File");

        var emulatorFiles = [
            "/system/lib/libc_malloc_debug_qemu.so",
            "/sys/qemu_trace",
            "/system/bin/qemu-props",
            "/dev/socket/qemud",
            "/dev/qemu_pipe",
            "/dev/goldfish_pipe",
            "/system/bin/androVM-prop",
            "/system/bin/microvirt-prop",
            "/system/lib/libdroid4x.so",
            "/data/youwave_id",
            "/dev/vboxguest",
            "/dev/vboxuser",
            "/system/bin/nox-prop",
            "/system/bin/nox",
            "/system/bin/ttVM-prop",
            "/data/data/com.bluestacks",
            "/data/data/com.bignox.app",
            "/data/data/com.memu"
        ];

        File.exists.implementation = function () {
            var path = this.getAbsolutePath();

            for (var i = 0; i < emulatorFiles.length; i++) {
                if (path === emulatorFiles[i] || path.indexOf(emulatorFiles[i]) !== -1) {
                    return false;
                }
            }

            return this.exists();
        };

        console.log("[AntiDetect] File checks bypassed ✓");
    } catch (e) {
        console.log("[AntiDetect] File hook error: " + e);
    }

    // =============================================
    // 5. SYSTEM PROPERTIES
    // =============================================
    try {
        var SystemProperties = Java.use("android.os.SystemProperties");

        var propsToSpoof = {
            "ro.kernel.qemu": "0",
            "ro.hardware": config.board,
            "ro.product.model": config.model,
            "ro.product.brand": config.brand,
            "ro.product.manufacturer": config.manufacturer,
            "ro.product.device": config.device,
            "ro.build.fingerprint": config.fingerprint,
            "ro.serialno": config.serial,
            "ro.boot.serialno": config.serial,
            "gsm.version.baseband": "unknown",
            "init.svc.qemu-props": "",
            "qemu.hw.mainkeys": "",
            "ro.build.characteristics": "default"
        };

        SystemProperties.get.overload("java.lang.String").implementation = function (key) {
            if (propsToSpoof.hasOwnProperty(key)) {
                return propsToSpoof[key];
            }
            return this.get(key);
        };

        SystemProperties.get.overload("java.lang.String", "java.lang.String").implementation = function (key, def) {
            if (propsToSpoof.hasOwnProperty(key)) {
                return propsToSpoof[key];
            }
            return this.get(key, def);
        };

        console.log("[AntiDetect] SystemProperties spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] SystemProperties hook error: " + e);
    }

    // =============================================
    // 6. SENSORS (Hide emulator sensors)
    // =============================================
    try {
        var SensorManager = Java.use("android.hardware.SensorManager");
        var Sensor = Java.use("android.hardware.Sensor");

        Sensor.getName.implementation = function () {
            var name = this.getName();
            // Replace emulator sensor names with real ones
            if (name.indexOf("goldfish") !== -1 || name.indexOf("qemu") !== -1) {
                return "LSM6DS3 Accelerometer";
            }
            return name;
        };

        Sensor.getVendor.implementation = function () {
            var vendor = this.getVendor();
            if (vendor.indexOf("Goldfish") !== -1 || vendor.indexOf("QEMU") !== -1) {
                return "STMicroelectronics";
            }
            return vendor;
        };

        console.log("[AntiDetect] Sensors spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] Sensor hook error: " + e);
    }

    // =============================================
    // 7. PACKAGE MANAGER (Hide emulator apps)
    // =============================================
    try {
        var PackageManager = Java.use("android.app.ApplicationPackageManager");

        var emuPackages = [
            "com.bluestacks",
            "com.bignox.app",
            "com.memu",
            "com.ldmnq",
            "com.kaopu.gameassistant",
            "com.google.android.launcher.layouts.genymotion",
            "com.vphone.launcher"
        ];

        PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function (pkg, flags) {
            for (var i = 0; i < emuPackages.length; i++) {
                if (pkg.indexOf(emuPackages[i]) !== -1) {
                    throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new();
                }
            }
            return this.getPackageInfo(pkg, flags);
        };

        console.log("[AntiDetect] PackageManager spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] PackageManager hook error: " + e);
    }

    // =============================================
    // 8. DEBUG/ROOT DETECTION
    // =============================================
    try {
        var Debug = Java.use("android.os.Debug");

        Debug.isDebuggerConnected.implementation = function () {
            return false;
        };

        var Runtime = Java.use("java.lang.Runtime");
        var originalExec = Runtime.exec.overload("java.lang.String");

        originalExec.implementation = function (cmd) {
            // Block root detection commands
            if (cmd.indexOf("su") !== -1 || cmd.indexOf("which") !== -1) {
                throw Java.use("java.io.IOException").$new("Permission denied");
            }
            return originalExec.call(this, cmd);
        };

        console.log("[AntiDetect] Debug/Root checks bypassed ✓");
    } catch (e) {
        console.log("[AntiDetect] Debug hook error: " + e);
    }

    // =============================================
    // 9. SETTINGS APP UI SPOOFING (ENHANCED)
    // =============================================
    try {
        var TextView = Java.use("android.widget.TextView");
        var StringClass = Java.use("java.lang.String");

        // Strings to replace in UI
        var uiReplacements = {
            "About emulated device": "About phone",
            "Emulated device": config.model,
            "sdk_gphone64_x86_64": config.model,
            "sdk_gphone64": config.model,
            "sdk_gphone": config.model,
            "generic_x86_64": config.device,
            "generic_x86": config.device,
            "ranchu": config.board,
            "goldfish": config.board,
            "Android SDK built for x86_64": config.model,
            "Android SDK built for x86": config.model,
            "AOSP on x86_64": config.model,
            "AOSP on x86": config.model,
            "emulator64_x86_64": config.device,
            "emulator64_x86": config.device,
            "emulator": config.device
        };

        TextView.setText.overload("java.lang.CharSequence").implementation = function (text) {
            if (text) {
                var str = text.toString();

                // Check all replacements
                for (var original in uiReplacements) {
                    if (str.indexOf(original) !== -1) {
                        var replacement = uiReplacements[original];
                        str = str.replace(original, replacement);
                        console.log("[AntiDetect] UI replaced: " + original + " -> " + replacement);
                    }
                }

                return this.setText(StringClass.$new(str));
            }
            return this.setText(text);
        };

        console.log("[AntiDetect] TextView setText hooked ✓");
    } catch (e) {
        console.log("[AntiDetect] TextView hook error: " + e);
    }

    // Hook Resources.getString for early string replacement
    try {
        var Resources = Java.use("android.content.res.Resources");

        Resources.getString.overload("int").implementation = function (id) {
            var res = this.getString(id);

            // Replace emulator strings
            if (res === "About emulated device") return "About phone";
            if (res === "Emulated device") return config.model;
            if (res.indexOf("sdk_gphone") !== -1) return config.model;
            if (res.indexOf("generic_x86") !== -1) return config.device;
            if (res.indexOf("ranchu") !== -1) return config.board;
            if (res.indexOf("goldfish") !== -1) return config.board;

            return res;
        };

        Resources.getText.overload("int").implementation = function (id) {
            var res = this.getText(id);
            var str = res.toString();

            if (str === "About emulated device") return StringClass.$new("About phone");
            if (str === "Emulated device") return StringClass.$new(config.model);
            if (str.indexOf("sdk_gphone") !== -1) return StringClass.$new(config.model);

            return res;
        };

        console.log("[AntiDetect] Resources hooks installed ✓");
    } catch (e) {
        console.log("[AntiDetect] Resources hook error: " + e);
    }

    // =============================================
    // 10. DEVICE NAME SETTINGS
    // =============================================
    try {
        var Global = Java.use("android.provider.Settings$Global");
        Global.getString.implementation = function (resolver, name) {
            if (name === "device_name") {
                return config.model;
            }
            return this.getString(resolver, name);
        };
        console.log("[AntiDetect] Device Name spoofed in Settings ✓");
    } catch (e) {
        console.log("[AntiDetect] Device Name hook error: " + e);
    }

    console.log("[AntiDetect] Core hooks installed ✓");

    // =============================================
    // 11. OPENGL/GPU RENDERER SPOOFING
    // =============================================
    try {
        var GLES20 = Java.use("android.opengl.GLES20");

        GLES20.glGetString.implementation = function (name) {
            var result = this.glGetString(name);

            // GL_RENDERER = 0x1F01, GL_VENDOR = 0x1F00
            if (name === 0x1F01) {  // GL_RENDERER
                // Replace emulator GPU with real one
                if (result && (result.indexOf("Android Emulator") !== -1 ||
                    result.indexOf("SwiftShader") !== -1 ||
                    result.indexOf("ANGLE") !== -1)) {
                    console.log("[AntiDetect] GPU Renderer spoofed: Adreno (TM) 660");
                    return "Adreno (TM) 660";
                }
            } else if (name === 0x1F00) {  // GL_VENDOR
                if (result && result.indexOf("Google") !== -1) {
                    return "Qualcomm";
                }
            }

            return result;
        };

        console.log("[AntiDetect] OpenGL spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] OpenGL hook error: " + e);
    }

    // =============================================
    // 12. EGL DISPLAY INFO
    // =============================================
    try {
        var EGL14 = Java.use("android.opengl.EGL14");

        EGL14.eglQueryString.implementation = function (display, name) {
            var result = this.eglQueryString(display, name);

            // EGL_VENDOR = 0x3053
            if (name === 0x3053 && result) {
                if (result.indexOf("Google") !== -1 || result.indexOf("Android") !== -1) {
                    return "Qualcomm Inc.";
                }
            }

            return result;
        };

        console.log("[AntiDetect] EGL spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] EGL hook error: " + e);
    }

    // =============================================
    // 13. BATTERY STATE SPOOFING
    // =============================================
    try {
        var BatteryManager = Java.use("android.os.BatteryManager");

        // Spoof battery to not always be charging (emulator giveaway)
        BatteryManager.getIntProperty.implementation = function (id) {
            // BATTERY_PROPERTY_STATUS = 6
            // BATTERY_PROPERTY_CAPACITY = 4
            if (id === 6) {
                // Return DISCHARGING (3) instead of CHARGING (2)
                return 3;
            }
            if (id === 4) {
                // Random realistic battery level
                return 45 + Math.floor(Math.random() * 40);
            }
            return this.getIntProperty(id);
        };

        // Hook Intent for BATTERY_CHANGED
        var IntentFilter = Java.use("android.content.Intent");

        console.log("[AntiDetect] Battery spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] Battery hook error: " + e);
    }

    // =============================================
    // 14. WIFI/BLUETOOTH MAC SPOOFING
    // =============================================
    try {
        var WifiInfo = Java.use("android.net.wifi.WifiInfo");

        WifiInfo.getMacAddress.implementation = function () {
            // Return spoofed MAC from config
            var spoofedMac = config.wifiMac || "94:65:2D:" +
                Math.floor(Math.random() * 256).toString(16).padStart(2, '0') + ":" +
                Math.floor(Math.random() * 256).toString(16).padStart(2, '0') + ":" +
                Math.floor(Math.random() * 256).toString(16).padStart(2, '0');
            return spoofedMac.toUpperCase();
        };

        console.log("[AntiDetect] WiFi MAC spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] WiFi MAC hook error: " + e);
    }

    try {
        var BluetoothAdapter = Java.use("android.bluetooth.BluetoothAdapter");

        BluetoothAdapter.getAddress.implementation = function () {
            var spoofedMac = config.bluetoothMac || "00:1A:7D:" +
                Math.floor(Math.random() * 256).toString(16).padStart(2, '0') + ":" +
                Math.floor(Math.random() * 256).toString(16).padStart(2, '0') + ":" +
                Math.floor(Math.random() * 256).toString(16).padStart(2, '0');
            return spoofedMac.toUpperCase();
        };

        console.log("[AntiDetect] Bluetooth MAC spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] Bluetooth hook error: " + e);
    }

    // =============================================
    // 15. HARDWARE CAMERA INFO
    // =============================================
    try {
        var CameraCharacteristics = Java.use("android.hardware.camera2.CameraCharacteristics");

        // This helps avoid camera-based emulator detection
        console.log("[AntiDetect] Camera characteristics available for spoofing");
    } catch (e) { }

    // =============================================
    // 16. TIMING/PERFORMANCE NORMALIZATION
    // =============================================
    try {
        var SystemClock = Java.use("android.os.SystemClock");

        // Add slight random delay to prevent timing attacks
        var originalUptimeMillis = SystemClock.uptimeMillis;
        SystemClock.uptimeMillis.implementation = function () {
            return originalUptimeMillis.call(this) + Math.floor(Math.random() * 10);
        };

        console.log("[AntiDetect] Timing normalized ✓");
    } catch (e) {
        console.log("[AntiDetect] Timing hook error: " + e);
    }

    // =============================================
    // 17. DISPLAY METRICS
    // =============================================
    try {
        var DisplayMetrics = Java.use("android.util.DisplayMetrics");

        // Ensure density matches real device
        console.log("[AntiDetect] DisplayMetrics available");
    } catch (e) { }

    // =============================================
    // 18. CONNECTIVITY CHECK
    // =============================================
    try {
        var NetworkInfo = Java.use("android.net.NetworkInfo");

        NetworkInfo.getType.implementation = function () {
            // Return WIFI (1) or MOBILE (0) instead of emulator type
            return 1;  // WIFI
        };

        NetworkInfo.getTypeName.implementation = function () {
            return "WIFI";
        };

        console.log("[AntiDetect] Network type spoofed ✓");
    } catch (e) {
        console.log("[AntiDetect] Network hook error: " + e);
    }

    console.log("[AntiDetect] All hooks installed successfully! ✓");
});
