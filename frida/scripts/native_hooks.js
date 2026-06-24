/**
 * Native Hooks - C-level detection bypass for Android emulator
 * Intercepts libc functions to hide emulator traces
 */

// Files that indicate emulator
var emulatorFiles = [
    "/system/lib/libc_malloc_debug_qemu.so",
    "/sys/qemu_trace",
    "/system/bin/qemu-props",
    "/dev/socket/qemud",
    "/dev/qemu_pipe",
    "/dev/goldfish_pipe",
    "/dev/goldfish_audio",
    "/dev/goldfish_sync",
    "/dev/goldfish_events",
    "/system/bin/androVM-prop",
    "/system/bin/microvirt-prop",
    "/system/lib/libdroid4x.so",
    "/data/youwave_id",
    "/dev/vboxguest",
    "/dev/vboxuser",
    "/system/bin/nox-prop",
    "/system/bin/nox",
    "/system/bin/ttVM-prop",
    "/ueventd.android_x86.rc",
    "/x86.prop",
    "/ueventd.ttVM_x86.rc",
    "/init.ttVM_x86.rc",
    "/init.vbox86.rc",
    "/init.goldfish.rc",
    "/init.ranchu.rc",
    "/fstab.goldfish",
    "/fstab.ranchu",
    "/sys/bus/pci",
    "/dev/ttyGF0",
    "/dev/ttyGF1"
];

// Strings that indicate emulator in /proc/cpuinfo
var cpuInfoReplacements = {
    "QEMU Virtual CPU": "Qualcomm Kryo 585",
    "Goldfish": "Qualcomm Technologies, Inc",
    "ranchu": "kona",
    "generic_x86_64": "kona",
    "Android Emulator": "SM-G998B"
};

// Config to be replaced by Python
var spoofedConfig = {
    cpuModel: "{{CPU_MODEL}}",
    cpuHardware: "{{CPU_HARDWARE}}",
    cpuFeatures: "{{CPU_FEATURES}}"
};

console.log("[NativeHooks] Initializing native-level detection bypass...");

// =============================================
// 1. LIBC ACCESS() HOOK
// =============================================
try {
    var accessPtr = Module.findExportByName("libc.so", "access");
    if (accessPtr) {
        Interceptor.attach(accessPtr, {
            onEnter: function (args) {
                this.path = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                if (this.path) {
                    for (var i = 0; i < emulatorFiles.length; i++) {
                        if (this.path.indexOf(emulatorFiles[i]) !== -1) {
                            retval.replace(-1);
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] access() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] access() hook error: " + e);
}

// =============================================
// 2. LIBC FOPEN() HOOK
// =============================================
try {
    var fopenPtr = Module.findExportByName("libc.so", "fopen");
    if (fopenPtr) {
        Interceptor.attach(fopenPtr, {
            onEnter: function (args) {
                this.path = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                if (this.path) {
                    for (var i = 0; i < emulatorFiles.length; i++) {
                        if (this.path.indexOf(emulatorFiles[i]) !== -1) {
                            retval.replace(ptr(0));  // Return NULL
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] fopen() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] fopen() hook error: " + e);
}

// =============================================
// 3. LIBC OPEN() HOOK
// =============================================
try {
    var openPtr = Module.findExportByName("libc.so", "open");
    if (openPtr) {
        Interceptor.attach(openPtr, {
            onEnter: function (args) {
                this.path = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                if (this.path) {
                    for (var i = 0; i < emulatorFiles.length; i++) {
                        if (this.path.indexOf(emulatorFiles[i]) !== -1) {
                            retval.replace(-1);  // Return error
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] open() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] open() hook error: " + e);
}

// =============================================
// 4. LIBC STAT() HOOK
// =============================================
try {
    var statPtr = Module.findExportByName("libc.so", "stat");
    if (statPtr) {
        Interceptor.attach(statPtr, {
            onEnter: function (args) {
                this.path = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                if (this.path) {
                    for (var i = 0; i < emulatorFiles.length; i++) {
                        if (this.path.indexOf(emulatorFiles[i]) !== -1) {
                            retval.replace(-1);
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] stat() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] stat() hook error: " + e);
}

// =============================================
// 5. LIBC LSTAT() HOOK
// =============================================
try {
    var lstatPtr = Module.findExportByName("libc.so", "lstat");
    if (lstatPtr) {
        Interceptor.attach(lstatPtr, {
            onEnter: function (args) {
                this.path = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                if (this.path) {
                    for (var i = 0; i < emulatorFiles.length; i++) {
                        if (this.path.indexOf(emulatorFiles[i]) !== -1) {
                            retval.replace(-1);
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] lstat() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] lstat() hook error: " + e);
}

// =============================================
// 6. READ() HOOK FOR /proc/cpuinfo SPOOFING
// =============================================
try {
    var readPtr = Module.findExportByName("libc.so", "read");
    if (readPtr) {
        var cpuinfoFds = {};

        // Track opens of /proc/cpuinfo
        var openPtrForCpu = Module.findExportByName("libc.so", "open");
        Interceptor.attach(openPtrForCpu, {
            onEnter: function (args) {
                this.path = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                if (this.path && this.path.indexOf("/proc/cpuinfo") !== -1) {
                    cpuinfoFds[retval.toInt32()] = true;
                }
            }
        });

        Interceptor.attach(readPtr, {
            onEnter: function (args) {
                this.fd = args[0].toInt32();
                this.buf = args[1];
                this.count = args[2].toInt32();
            },
            onLeave: function (retval) {
                if (cpuinfoFds[this.fd] && retval.toInt32() > 0) {
                    try {
                        var content = this.buf.readUtf8String(retval.toInt32());
                        var modified = content;

                        // Replace emulator indicators
                        for (var key in cpuInfoReplacements) {
                            if (modified.indexOf(key) !== -1) {
                                modified = modified.replace(new RegExp(key, 'g'), cpuInfoReplacements[key]);
                            }
                        }

                        if (modified !== content) {
                            this.buf.writeUtf8String(modified);
                        }
                    } catch (e) { }
                }
            }
        });
        console.log("[NativeHooks] /proc/cpuinfo spoofing hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] cpuinfo hook error: " + e);
}

// =============================================
// 7. SYSTEM_PROPERTY_GET HOOK
// =============================================
try {
    var propGetPtr = Module.findExportByName("libc.so", "__system_property_get");
    if (propGetPtr) {
        var propReplacements = {
            "ro.kernel.qemu": "0",
            "ro.boot.qemu": "0",
            "ro.hardware": "qcom",
            "ro.product.cpu.abilist": "arm64-v8a,armeabi-v7a,armeabi",
            "ro.arch": "arm64",
            "init.svc.qemu-props": "",
            "qemu.hw.mainkeys": "",
            "ro.build.characteristics": "default"
        };

        Interceptor.attach(propGetPtr, {
            onEnter: function (args) {
                this.name = args[0].readUtf8String();
                this.value = args[1];
            },
            onLeave: function (retval) {
                if (this.name && propReplacements.hasOwnProperty(this.name)) {
                    var replacement = propReplacements[this.name];
                    this.value.writeUtf8String(replacement);
                    retval.replace(replacement.length);
                }
            }
        });
        console.log("[NativeHooks] __system_property_get hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] property_get hook error: " + e);
}

// =============================================
// 8. DLOPEN HOOK - HIDE EMULATOR LIBRARIES
// =============================================
try {
    var dlopenPtr = Module.findExportByName("libdl.so", "dlopen");
    if (dlopenPtr) {
        var blockedLibs = [
            "libqemu",
            "libgoldfish",
            "libvbox",
            "libnox",
            "libmemu"
        ];

        Interceptor.attach(dlopenPtr, {
            onEnter: function (args) {
                if (args[0]) {
                    this.libPath = args[0].readUtf8String();
                }
            },
            onLeave: function (retval) {
                if (this.libPath) {
                    for (var i = 0; i < blockedLibs.length; i++) {
                        if (this.libPath.indexOf(blockedLibs[i]) !== -1) {
                            retval.replace(ptr(0));
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] dlopen() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] dlopen hook error: " + e);
}

// =============================================
// 9. STRCASECMP/STRSTR HOOKS FOR STRING CHECKS
// =============================================
try {
    var strstrPtr = Module.findExportByName("libc.so", "strstr");
    if (strstrPtr) {
        var blockedStrings = [
            "goldfish",
            "ranchu",
            "qemu",
            "vbox",
            "genymotion",
            "nox"
        ];

        Interceptor.attach(strstrPtr, {
            onEnter: function (args) {
                if (args[1]) {
                    this.needle = args[1].readUtf8String().toLowerCase();
                }
            },
            onLeave: function (retval) {
                if (this.needle && !retval.isNull()) {
                    for (var i = 0; i < blockedStrings.length; i++) {
                        if (this.needle.indexOf(blockedStrings[i]) !== -1) {
                            retval.replace(ptr(0));
                            return;
                        }
                    }
                }
            }
        });
        console.log("[NativeHooks] strstr() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] strstr hook error: " + e);
}

// =============================================
// 10. GETENV HOOK
// =============================================
try {
    var getenvPtr = Module.findExportByName("libc.so", "getenv");
    if (getenvPtr) {
        Interceptor.attach(getenvPtr, {
            onEnter: function (args) {
                this.name = args[0].readUtf8String();
            },
            onLeave: function (retval) {
                // Hide ANDROID_EMULATOR env var
                if (this.name && this.name.indexOf("EMULATOR") !== -1) {
                    retval.replace(ptr(0));
                }
            }
        });
        console.log("[NativeHooks] getenv() hooked ✓");
    }
} catch (e) {
    console.log("[NativeHooks] getenv hook error: " + e);
}

console.log("[NativeHooks] All native hooks installed successfully! ✓");
