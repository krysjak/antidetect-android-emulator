"""
Profile Generator - Generate unique device identities with valid checksums
"""
import random
import string
import hashlib
from datetime import datetime


def generate_imei():
    """Generate valid IMEI with correct Luhn checksum"""
    # TAC (Type Allocation Code) - first 8 digits
    tac_list = [
        "35291505",  # Samsung
        "35694210",  # Samsung
        "86776502",  # Xiaomi
        "86771305",  # Xiaomi
        "35332407",  # Google Pixel
        "35260100",  # OnePlus
        "86697903",  # Huawei
    ]
    tac = random.choice(tac_list)
    
    # Serial number - next 6 digits
    serial = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Calculate Luhn checksum
    imei_without_check = tac + serial
    check_digit = calculate_luhn_checksum(imei_without_check)
    
    return imei_without_check + str(check_digit)


def calculate_luhn_checksum(number_string):
    """Calculate Luhn checksum digit"""
    digits = [int(d) for d in number_string]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    
    return (10 - (checksum % 10)) % 10


def generate_serial_number(brand="Samsung"):
    """Generate realistic serial number based on brand"""
    if brand.lower() == "samsung":
        # Samsung: R5CT + 8 chars
        prefix = random.choice(["R5CT", "RF8R", "R3CM", "R9UE"])
        chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return prefix + chars
    elif brand.lower() in ["xiaomi", "redmi", "poco"]:
        # Xiaomi: numbers/letters mix
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    elif brand.lower() == "google":
        # Pixel: alphanumeric
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    elif brand.lower() == "oneplus":
        # OnePlus format
        return "NB" + ''.join(random.choices(string.digits, k=10))
    else:
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


def generate_android_id():
    """Generate Android ID (16 hex characters)"""
    return ''.join(random.choices('0123456789abcdef', k=16))


def generate_mac_address():
    """Generate random MAC address"""
    # Use valid OUI prefixes for major vendors
    oui_list = [
        "00:1A:7D",  # Samsung
        "64:A2:F9",  # Samsung
        "9C:5C:F9",  # Xiaomi
        "28:6C:07",  # Xiaomi
        "F4:F5:E8",  # Google
        "94:65:2D",  # OnePlus
    ]
    oui = random.choice(oui_list)
    nic = ':'.join(['%02x' % random.randint(0, 255) for _ in range(3)])
    return f"{oui}:{nic}"


def generate_wifi_ssid():
    """Generate realistic nearby WiFi SSIDs"""
    prefixes = ["NETGEAR", "Linksys", "TP-LINK", "ASUS", "Home", "Apt", "Wifi", "5G"]
    suffixes = ["_5G", "_Guest", "_2.4G", "-5GHz", ""]
    
    ssids = []
    for _ in range(random.randint(3, 8)):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        number = random.randint(1, 999)
        ssids.append(f"{prefix}{number}{suffix}")
    
    return ssids


def generate_gsf_id():
    """Generate Google Services Framework ID"""
    return ''.join(random.choices('0123456789abcdef', k=16))


def generate_advertising_id():
    """Generate Google Advertising ID (UUID format)"""
    return '-'.join([
        ''.join(random.choices('0123456789abcdef', k=8)),
        ''.join(random.choices('0123456789abcdef', k=4)),
        '4' + ''.join(random.choices('0123456789abcdef', k=3)),
        random.choice(['8', '9', 'a', 'b']) + ''.join(random.choices('0123456789abcdef', k=3)),
        ''.join(random.choices('0123456789abcdef', k=12)),
    ])


def generate_device_identity(model_profile):
    """Generate complete device identity based on model profile"""
    brand = model_profile.get("brand", "Samsung")
    
    identity = {
        # Hardware IDs
        "imei": generate_imei(),
        "imei2": generate_imei(),  # Dual SIM
        "serial": generate_serial_number(brand),
        "android_id": generate_android_id(),
        "mac_address": generate_mac_address(),
        "wifi_mac": generate_mac_address(),
        "bluetooth_mac": generate_mac_address(),
        
        # Google IDs
        "gsf_id": generate_gsf_id(),
        "advertising_id": generate_advertising_id(),
        
        # Device info from profile
        "brand": brand,
        "manufacturer": brand,
        "model": model_profile.get("model", "Unknown"),
        "device": model_profile.get("device", "generic"),
        "board": model_profile.get("board", "unknown"),
        "fingerprint": model_profile.get("fingerprint", ""),
        "product": model_profile.get("device", "generic"),
        
        # Build info
        "build_id": generate_build_id(),
        "build_number": generate_build_number(brand),
        
        # Network info
        "operator": random.choice(["Vodafone", "T-Mobile", "AT&T", "O2", "Orange"]),
        "operator_code": random.choice(["310260", "310410", "310120", "23415", "20801"]),
        
        # Nearby WiFi (for fingerprinting)
        "nearby_wifi": generate_wifi_ssid(),
        
        # Timestamps
        "first_boot": int(datetime.now().timestamp()) - random.randint(86400 * 30, 86400 * 365),
        "generated_at": datetime.now().isoformat(),
    }
    
    return identity


def generate_build_id():
    """Generate Android build ID"""
    prefixes = ["UP1A", "UD1A", "UKQ1", "TP1A", "TQ3A"]
    return f"{random.choice(prefixes)}.{random.randint(230101, 241231)}.{random.randint(1, 99):03d}"


def generate_build_number(brand):
    """Generate brand-specific build number"""
    if brand.lower() == "samsung":
        return f"S{random.randint(900, 928)}BXXS{random.randint(1, 9)}AXL{random.randint(1, 9)}"
    elif brand.lower() in ["xiaomi", "redmi", "poco"]:
        return f"V{random.randint(14, 16)}.0.{random.randint(1, 30)}.0.UNACNXM"
    elif brand.lower() == "google":
        return f"{random.randint(10000000, 12000000)}"
    else:
        return f"RKQ1.{random.randint(200101, 241231)}.002"


def generate_gpu_renderer(brand, model_name):
    """Generate realistic GPU renderer string for device"""
    gpu_map = {
        "Samsung": {
            "S24": "Mali-G720",
            "S23": "Adreno (TM) 740",
            "S22": "Xclipse 920",
            "A54": "Mali-G68",
            "default": "Adreno (TM) 660"
        },
        "Xiaomi": {
            "14": "Adreno (TM) 750",
            "13": "Adreno (TM) 740",
            "default": "Adreno (TM) 660"
        },
        "Google": {
            "Pixel 8": "Mali-G715",
            "Pixel 7": "Mali-G710",
            "default": "Mali-G710"
        },
        "OnePlus": {
            "12": "Adreno (TM) 750",
            "11": "Adreno (TM) 740",
            "default": "Adreno (TM) 660"
        }
    }
    
    brand_gpus = gpu_map.get(brand, {"default": "Adreno (TM) 660"})
    
    for key, renderer in brand_gpus.items():
        if key != "default" and key.lower() in model_name.lower():
            return renderer
    
    return brand_gpus.get("default", "Adreno (TM) 660")


def generate_gpu_vendor(renderer):
    """Get GPU vendor from renderer string"""
    if "Adreno" in renderer:
        return "Qualcomm"
    elif "Mali" in renderer:
        return "ARM"
    elif "Xclipse" in renderer:
        return "Samsung"
    else:
        return "Qualcomm"


def generate_battery_info(brand, model_name):
    """Generate realistic battery specifications"""
    battery_map = {
        "flagship": {"capacity": 5000, "technology": "Li-poly", "voltage": 4350},
        "midrange": {"capacity": 4500, "technology": "Li-ion", "voltage": 4200},
        "budget": {"capacity": 4000, "technology": "Li-ion", "voltage": 4100}
    }
    
    # Determine tier
    if any(x in model_name.lower() for x in ["ultra", "pro", "plus", "fold", "flip"]):
        tier = "flagship"
    elif any(x in model_name.lower() for x in ["a54", "a34", "note", "nord"]):
        tier = "midrange"
    else:
        tier = "flagship"  # Default to flagship
    
    specs = battery_map[tier]
    return {
        "capacity_mah": specs["capacity"],
        "technology": specs["technology"],
        "voltage_mv": specs["voltage"],
        "health": "Good",
        "temperature": round(random.uniform(25, 32), 1)
    }


def generate_cpu_info(brand, board):
    """Generate CPU information"""
    cpu_map = {
        "kalama": {"model": "Snapdragon 8 Gen 2", "cores": 8, "hardware": "qcom"},
        "pineapple": {"model": "Snapdragon 8 Gen 3", "cores": 8, "hardware": "qcom"},
        "zuma": {"model": "Google Tensor G3", "cores": 9, "hardware": "zuma"},
        "gs201": {"model": "Google Tensor G2", "cores": 8, "hardware": "gs201"},
        "s5e9945": {"model": "Exynos 2400", "cores": 10, "hardware": "exynos"},
        "s5e9925": {"model": "Exynos 2200", "cores": 8, "hardware": "exynos"},
        "mt6985": {"model": "Dimensity 9200+", "cores": 8, "hardware": "mt6985"},
    }
    
    info = cpu_map.get(board, {"model": "Snapdragon 8 Gen 1", "cores": 8, "hardware": "qcom"})
    return info


def generate_bootloader(brand, model):
    """Generate bootloader version"""
    if brand.lower() == "samsung":
        return f"{model}XXS{random.randint(1, 9)}AW{random.choice(['A', 'B', 'C'])}{random.randint(1, 9)}"
    elif brand.lower() in ["xiaomi", "redmi", "poco"]:
        return f"V{random.randint(14, 16)}.0.{random.randint(1, 20)}.0"
    elif brand.lower() == "google":
        return f"slider-{random.randint(14, 16)}.0.0"
    elif brand.lower() == "oneplus":
        return f"{random.randint(14, 16)}.0.0.0"
    else:
        return "unknown"


def generate_baseband(brand):
    """Generate baseband/modem version"""
    if brand.lower() == "samsung":
        return f"S{random.randint(900, 928)}BXXS{random.randint(1, 9)}AW{random.choice(['A', 'B'])}{random.randint(1, 3)}"
    elif brand.lower() in ["xiaomi", "redmi", "poco"]:
        return f"MPSS.DE.{random.randint(3, 5)}.0.{random.randint(1, 3)}-{random.randint(1, 9)}"
    elif brand.lower() == "google":
        return f"g5300q-230525-{random.randint(230601, 241231)}-B-{random.randint(10000000, 12000000)}"
    else:
        return "unknown"


def generate_device_identity(model_profile, android_version="14"):
    """Generate complete device identity based on model profile"""
    brand = model_profile.get("brand", "Samsung")
    model = model_profile.get("model", "Unknown")
    model_name = model_profile.get("name", model)
    board = model_profile.get("board", "unknown")
    
    # Get GPU info
    gl_renderer = generate_gpu_renderer(brand, model_name)
    gl_vendor = generate_gpu_vendor(gl_renderer)
    
    # Get battery info
    battery = generate_battery_info(brand, model_name)
    
    # Get CPU info
    cpu = generate_cpu_info(brand, board)
    
    identity = {
        # Hardware IDs
        "imei": generate_imei(),
        "imei2": generate_imei(),  # Dual SIM
        "serial": generate_serial_number(brand),
        "android_id": generate_android_id(),
        "mac_address": generate_mac_address(),
        "wifi_mac": generate_mac_address(),
        "bluetooth_mac": generate_mac_address(),
        
        # Google IDs
        "gsf_id": generate_gsf_id(),
        "advertising_id": generate_advertising_id(),
        
        # Device info from profile
        "brand": brand,
        "manufacturer": brand,
        "model": model,
        "device": model_profile.get("device", "generic"),
        "board": board,
        "fingerprint": model_profile.get("fingerprint", ""),
        "product": model_profile.get("device", "generic"),
        
        # Build info
        "build_id": generate_build_id(),
        "build_number": generate_build_number(brand),
        "android_version": android_version,
        
        # GPU info
        "gl_renderer": gl_renderer,
        "gl_vendor": gl_vendor,
        "gl_version": f"OpenGL ES 3.2 V@0{random.randint(600, 800)}.0",
        
        # Battery info
        "battery_capacity": battery["capacity_mah"],
        "battery_technology": battery["technology"],
        "battery_health": battery["health"],
        
        # CPU info
        "cpu_model": cpu["model"],
        "cpu_cores": cpu["cores"],
        "cpu_hardware": cpu["hardware"],
        
        # Bootloader & Baseband
        "bootloader": generate_bootloader(brand, model),
        "baseband": generate_baseband(brand),
        
        # Network info
        "operator": random.choice(["Vodafone", "T-Mobile", "AT&T", "O2", "Orange"]),
        "operator_code": random.choice(["310260", "310410", "310120", "23415", "20801"]),
        
        # Nearby WiFi (for fingerprinting)
        "nearby_wifi": generate_wifi_ssid(),
        
        # Timestamps
        "first_boot": int(datetime.now().timestamp()) - random.randint(86400 * 30, 86400 * 365),
        "generated_at": datetime.now().isoformat(),
    }
    
    return identity

