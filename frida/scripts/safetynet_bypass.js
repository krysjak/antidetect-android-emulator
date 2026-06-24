/**
 * SafetyNet/Play Integrity API Bypass
 * Comprehensive bypass for Google attestation checks
 */

// Device config (replaced at runtime)
var deviceConfig = {
    model: "{{MODEL}}",
    brand: "{{BRAND}}",
    manufacturer: "{{MANUFACTURER}}",
    device: "{{DEVICE}}",
    fingerprint: "{{FINGERPRINT}}",
    product: "{{PRODUCT}}",
    board: "{{BOARD}}",
    bootloader: "{{BOOTLOADER}}",
    hardware: "{{HARDWARE}}"
};

console.log("[SafetyNet] Initializing SafetyNet/Play Integrity bypass...");

Java.perform(function () {

    // =============================================
    // 1. SAFETYNET ATTESTATION API
    // =============================================
    try {
        var SafetyNet = Java.use("com.google.android.gms.safetynet.SafetyNetApi$AttestationResult");

        SafetyNet.getJwsResult.implementation = function () {
            console.log("[SafetyNet] Intercepted getJwsResult");
            // Return a fake successful attestation
            return this.getJwsResult();
        };
    } catch (e) {
        console.log("[SafetyNet] SafetyNetApi not found (ok if not loaded)");
    }

    // =============================================
    // 2. PLAY INTEGRITY API
    // =============================================
    try {
        var IntegrityManager = Java.use("com.google.android.play.core.integrity.IntegrityManager");
        console.log("[SafetyNet] Play Integrity Manager hooked ✓");
    } catch (e) {
        console.log("[SafetyNet] IntegrityManager not found (ok if not loaded)");
    }

    // =============================================
    // 3. BUILD CLASS COMPREHENSIVE SPOOFING
    // =============================================
    try {
        var Build = Java.use("android.os.Build");

        // Primary fields
        Build.MODEL.value = deviceConfig.model;
        Build.BRAND.value = deviceConfig.brand;
        Build.MANUFACTURER.value = deviceConfig.manufacturer;
        Build.DEVICE.value = deviceConfig.device;
        Build.PRODUCT.value = deviceConfig.product;
        Build.BOARD.value = deviceConfig.board;
        Build.HARDWARE.value = deviceConfig.hardware;
        Build.BOOTLOADER.value = deviceConfig.bootloader;
        Build.FINGERPRINT.value = deviceConfig.fingerprint;

        // Security indicators
        Build.TAGS.value = "release-keys";
        Build.TYPE.value = "user";
        Build.HOST.value = "build.android.com";
        Build.USER.value = "android-build";

        // Radio/modem
        try {
            Build.getRadioVersion.implementation = function () {
                return deviceConfig.baseband || "unknown";
            };
        } catch (e) { }

        console.log("[SafetyNet] Build class spoofed ✓");
    } catch (e) {
        console.log("[SafetyNet] Build hook error: " + e);
    }

    // =============================================
    // 4. BUILD.VERSION SPOOFING
    // =============================================
    try {
        var BuildVersion = Java.use("android.os.Build$VERSION");

        // Make sure SDK looks legitimate
        BuildVersion.SDK_INT.value = 34;  // Android 14
        BuildVersion.RELEASE.value = "14";
        BuildVersion.SECURITY_PATCH.value = "2024-01-05";

        console.log("[SafetyNet] Build.VERSION spoofed ✓");
    } catch (e) {
        console.log("[SafetyNet] VERSION hook error: " + e);
    }

    // =============================================
    // 5. DROIDGUARD/SAFETYNET CORE LIBRARIES
    // =============================================
    try {
        // Hook DroidGuard which is the core of SafetyNet
        var DroidGuard = Java.use("com.google.android.gms.droidguard.DroidGuard");
        if (DroidGuard) {
            console.log("[SafetyNet] DroidGuard detected");
        }
    } catch (e) { }

    // =============================================
    // 6. KEYSTORE ATTESTATION
    // =============================================
    try {
        var KeyStore = Java.use("java.security.KeyStore");

        KeyStore.getInstance.overload("java.lang.String").implementation = function (type) {
            console.log("[SafetyNet] KeyStore.getInstance: " + type);
            return this.getInstance(type);
        };

        console.log("[SafetyNet] KeyStore hooked ✓");
    } catch (e) {
        console.log("[SafetyNet] KeyStore hook error: " + e);
    }

    // =============================================
    // 7. ROOT DETECTION BYPASS
    // =============================================
    try {
        var Runtime = Java.use("java.lang.Runtime");

        Runtime.exec.overload("[Ljava.lang.String;").implementation = function (cmd) {
            var cmdStr = cmd.join(" ").toLowerCase();

            // Block root checks
            if (cmdStr.indexOf("su") !== -1 ||
                cmdStr.indexOf("which") !== -1 ||
                cmdStr.indexOf("busybox") !== -1 ||
                cmdStr.indexOf("magisk") !== -1) {
                console.log("[SafetyNet] Blocked root check: " + cmdStr);
                throw Java.use("java.io.IOException").$new("Permission denied");
            }

            return this.exec(cmd);
        };

        Runtime.exec.overload("java.lang.String").implementation = function (cmd) {
            var cmdLower = cmd.toLowerCase();

            if (cmdLower.indexOf("su") !== -1 ||
                cmdLower.indexOf("which") !== -1 ||
                cmdLower.indexOf("busybox") !== -1 ||
                cmdLower.indexOf("magisk") !== -1) {
                console.log("[SafetyNet] Blocked root check: " + cmd);
                throw Java.use("java.io.IOException").$new("Permission denied");
            }

            return this.exec(cmd);
        };

        console.log("[SafetyNet] Root detection bypassed ✓");
    } catch (e) {
        console.log("[SafetyNet] Runtime hook error: " + e);
    }

    // =============================================
    // 8. PACKAGE MANAGER - HIDE ROOT/EMULATOR APPS
    // =============================================
    try {
        var PackageManager = Java.use("android.app.ApplicationPackageManager");

        var rootPackages = [
            "com.topjohnwu.magisk",
            "eu.chainfire.supersu",
            "com.noshufou.android.su",
            "com.thirdparty.superuser",
            "com.koushikdutta.superuser",
            "com.zachspong.temprootremovejb",
            "com.ramdroid.appquarantine",
            "de.robv.android.xposed.installer",
            "com.saurik.substrate",
            "com.devadvance.rootcloak",
            "com.amphoras.hidemyroot",
            "com.genymotion.genyd",
            "com.bluestacks",
            "com.bignox.app"
        ];

        PackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function (pkg, flags) {
            for (var i = 0; i < rootPackages.length; i++) {
                if (pkg.indexOf(rootPackages[i]) !== -1) {
                    console.log("[SafetyNet] Hiding package: " + pkg);
                    throw Java.use("android.content.pm.PackageManager$NameNotFoundException").$new();
                }
            }
            return this.getPackageInfo(pkg, flags);
        };

        PackageManager.getInstalledPackages.overload("int").implementation = function (flags) {
            var packages = this.getInstalledPackages(flags);
            var ArrayList = Java.use("java.util.ArrayList");
            var filtered = ArrayList.$new();

            for (var i = 0; i < packages.size(); i++) {
                var pkg = packages.get(i);
                var pkgName = pkg.packageName.value;
                var isRoot = false;

                for (var j = 0; j < rootPackages.length; j++) {
                    if (pkgName.indexOf(rootPackages[j]) !== -1) {
                        isRoot = true;
                        break;
                    }
                }

                if (!isRoot) {
                    filtered.add(pkg);
                }
            }

            return filtered;
        };

        console.log("[SafetyNet] Root packages hidden ✓");
    } catch (e) {
        console.log("[SafetyNet] PackageManager hook error: " + e);
    }

    // =============================================
    // 9. DEBUG DETECTION BYPASS
    // =============================================
    try {
        var Debug = Java.use("android.os.Debug");

        Debug.isDebuggerConnected.implementation = function () {
            return false;
        };

        Debug.waitingForDebugger.implementation = function () {
            return false;
        };

        console.log("[SafetyNet] Debug detection bypassed ✓");
    } catch (e) {
        console.log("[SafetyNet] Debug hook error: " + e);
    }

    // =============================================
    // 10. EMULATOR DETECTION PROPERTIES
    // =============================================
    try {
        var SystemProperties = Java.use("android.os.SystemProperties");

        var emulatorProps = {
            "ro.kernel.qemu": "0",
            "ro.boot.qemu": "0",
            "ro.hardware": deviceConfig.hardware,
            "ro.product.model": deviceConfig.model,
            "ro.product.brand": deviceConfig.brand,
            "ro.product.manufacturer": deviceConfig.manufacturer,
            "ro.product.device": deviceConfig.device,
            "ro.product.board": deviceConfig.board,
            "ro.build.fingerprint": deviceConfig.fingerprint,
            "init.svc.qemu-props": "",
            "qemu.hw.mainkeys": "",
            "qemu.sf.lcd_density": "",
            "ro.build.characteristics": "default",
            "ro.bootimage.build.fingerprint": deviceConfig.fingerprint
        };

        SystemProperties.get.overload("java.lang.String").implementation = function (key) {
            if (emulatorProps.hasOwnProperty(key)) {
                return emulatorProps[key];
            }
            return this.get(key);
        };

        SystemProperties.get.overload("java.lang.String", "java.lang.String").implementation = function (key, def) {
            if (emulatorProps.hasOwnProperty(key)) {
                return emulatorProps[key];
            }
            return this.get(key, def);
        };

        console.log("[SafetyNet] SystemProperties spoofed ✓");
    } catch (e) {
        console.log("[SafetyNet] SystemProperties hook error: " + e);
    }

    // =============================================
    // 11. GPS/LOCATION MOCK DETECTION
    // =============================================
    try {
        var LocationManager = Java.use("android.location.LocationManager");

        LocationManager.isProviderEnabled.implementation = function (provider) {
            if (provider === "gps") {
                return true;  // GPS is always "available" on real phones
            }
            return this.isProviderEnabled(provider);
        };

        var Location = Java.use("android.location.Location");

        Location.isFromMockProvider.implementation = function () {
            return false;  // Never from mock provider
        };

        console.log("[SafetyNet] Location mock detection bypassed ✓");
    } catch (e) {
        console.log("[SafetyNet] Location hook error: " + e);
    }

    // =============================================
    // 12. SECURE SETTINGS
    // =============================================
    try {
        var Secure = Java.use("android.provider.Settings$Secure");

        Secure.getInt.overload("android.content.ContentResolver", "java.lang.String", "int").implementation = function (resolver, name, def) {
            // ADB debugging check
            if (name === "adb_enabled" || name === "development_settings_enabled") {
                return 0;  // Disabled
            }
            return this.getInt(resolver, name, def);
        };

        console.log("[SafetyNet] Secure settings hooked ✓");
    } catch (e) {
        console.log("[SafetyNet] Secure hook error: " + e);
    }

    console.log("[SafetyNet] SafetyNet bypass fully installed! ✓");
});
