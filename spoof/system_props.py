"""
System Properties Spoofing - Modify ro.* properties to hide emulator
"""


def generate_props_config(identity, brand, model):
    """Generate emulator config.ini properties for anti-detection"""
    props = []
    
    # Device identity properties
    props.append(f"ro.product.model={identity['model']}")
    props.append(f"ro.product.brand={identity['brand']}")
    props.append(f"ro.product.manufacturer={identity['manufacturer']}")
    props.append(f"ro.product.device={identity['device']}")
    props.append(f"ro.product.board={identity['board']}")
    props.append(f"ro.product.name={identity['product']}")
    
    # Partition specific spoofing
    for part in ['system', 'vendor', 'odm', 'product', 'system_ext']:
        props.append(f"ro.product.{part}.model={identity['model']}")
        props.append(f"ro.product.{part}.brand={identity['brand']}")
        props.append(f"ro.product.{part}.manufacturer={identity['manufacturer']}")
        props.append(f"ro.product.{part}.device={identity['device']}")
        props.append(f"ro.product.{part}.name={identity['product']}")

    # Build properties
    props.append(f"ro.build.fingerprint={identity['fingerprint']}")
    props.append(f"ro.build.id={identity['build_id']}")
    props.append(f"ro.build.display.id={identity['build_number']}")
    props.append(f"ro.build.version.incremental={identity['build_number']}")
    props.append(f"ro.build.description={identity['product']}-user {identity['android_version']} {identity['build_id']} {identity['build_number']} release-keys")
    
    # Hide emulator indicators
    props.append("ro.kernel.qemu=0")
    props.append("ro.kernel.qemu.gles=0")
    props.append("ro.hardware.audio.primary=")  # Hide goldfish
    props.append("ro.hardware=ranchu")  # Use ranchu instead of goldfish
    props.append("ro.boot.hardware=unknown")
    props.append("ro.arch=x86_64")
    props.append("ro.boot.qemu=0")
    
    # Hardware identifiers
    props.append(f"ro.serialno={identity['serial']}")
    props.append(f"ro.boot.serialno={identity['serial']}")
    props.append(f"gsm.version.baseband={identity['build_number']}")
    
    # Network
    props.append(f"gsm.sim.operator.alpha={identity['operator']}")
    props.append(f"gsm.sim.operator.numeric={identity['operator_code']}")
    props.append(f"gsm.operator.alpha={identity['operator']}")
    
    return '\n'.join(props)


def get_adb_spoof_commands(identity):
    """Get ADB commands to spoof properties at runtime"""
    commands = []
    
    # Set system properties
    props = {
        "ro.product.model": identity["model"],
        "ro.product.brand": identity["brand"],
        "ro.product.manufacturer": identity["manufacturer"],
        "ro.product.device": identity["device"],
        "ro.serialno": identity["serial"],
        "ro.kernel.qemu": "0",
        "ro.hardware": identity["board"],
        "ro.bootimage.build.fingerprint": identity["fingerprint"],
        "ro.build.fingerprint": identity["fingerprint"],
    }
    
    for key, value in props.items():
        commands.append(f"setprop {key} {value}")
    
    return commands


EMULATOR_DETECTION_PROPS = [
    # Properties commonly checked for emulator detection
    "ro.kernel.qemu",
    "ro.hardware",
    "ro.boot.qemu",
    "init.svc.qemu-props",
    "qemu.sf.lcd_density",
    "qemu.hw.mainkeys",
    "ro.bootimage.build.fingerprint",
    "ro.build.characteristics",
    "ro.product.cpu.abilist",
    "gsm.version.baseband",
    "gsm.version.ril-impl",
]

EMULATOR_INDICATORS = {
    # Files that indicate emulator
    "files": [
        "/system/bin/qemu-props",
        "/system/lib/libc_malloc_debug_qemu.so",
        "/dev/socket/qemud",
        "/dev/qemu_pipe",
        "/system/bin/androVM-props",
        "/system/bin/microvirt-prop",
        "/system/lib/libdroid4x.so",
        "/data/youwave_id",
        "/dev/vboxguest",
        "/dev/vboxuser",
    ],
    # Processes that indicate emulator
    "processes": [
        "qemu-props",
        "qemud",
        "goldfish",
    ],
    # Package names of known emulators
    "packages": [
        "com.bluestacks",
        "com.bignox.app",
        "com.memu",
        "com.ldmnq",
        "com.kaopu.gameassistant",
    ],
}
