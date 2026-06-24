"""
Device Profiles - Real device specifications database
"""

# Samsung Devices
SAMSUNG_DEVICES = [
    # Galaxy S24 Series
    {"name": "Samsung Galaxy S24 Ultra", "brand": "Samsung", "model": "SM-S928B", "device": "e2s", "board": "s5e9945", "fingerprint": "samsung/e2sxxx/e2s:14/UP1A.231005.007/S928BXXS1AXL1:user/release-keys"},
    {"name": "Samsung Galaxy S24+", "brand": "Samsung", "model": "SM-S926B", "device": "e2q", "board": "s5e9945", "fingerprint": "samsung/e2qxxx/e2q:14/UP1A.231005.007/S926BXXS1AXL1:user/release-keys"},
    {"name": "Samsung Galaxy S24", "brand": "Samsung", "model": "SM-S921B", "device": "e2s", "board": "s5e9945", "fingerprint": "samsung/e2sxxx/e2s:14/UP1A.231005.007/S921BXXS1AXL1:user/release-keys"},
    
    # Galaxy S23 Series
    {"name": "Samsung Galaxy S23 Ultra", "brand": "Samsung", "model": "SM-S918B", "device": "dm3q", "board": "kalama", "fingerprint": "samsung/dm3qxxx/dm3q:14/UP1A.231005.007/S918BXXS5BXAA:user/release-keys"},
    {"name": "Samsung Galaxy S23+", "brand": "Samsung", "model": "SM-S916B", "device": "dm2q", "board": "kalama", "fingerprint": "samsung/dm2qxxx/dm2q:14/UP1A.231005.007/S916BXXS5BXAA:user/release-keys"},
    {"name": "Samsung Galaxy S23", "brand": "Samsung", "model": "SM-S911B", "device": "dm1q", "board": "kalama", "fingerprint": "samsung/dm1qxxx/dm1q:14/UP1A.231005.007/S911BXXS5BXAA:user/release-keys"},
    
    # Galaxy S22 Series
    {"name": "Samsung Galaxy S22 Ultra", "brand": "Samsung", "model": "SM-S908B", "device": "b0q", "board": "s5e9925", "fingerprint": "samsung/b0qxxx/b0q:14/UP1A.231005.007/S908BXXS9CXL1:user/release-keys"},
    {"name": "Samsung Galaxy S22+", "brand": "Samsung", "model": "SM-S906B", "device": "g0q", "board": "s5e9925", "fingerprint": "samsung/g0qxxx/g0q:14/UP1A.231005.007/S906BXXS9CXL1:user/release-keys"},
    {"name": "Samsung Galaxy S22", "brand": "Samsung", "model": "SM-S901B", "device": "r0q", "board": "s5e9925", "fingerprint": "samsung/r0qxxx/r0q:14/UP1A.231005.007/S901BXXS9CXL1:user/release-keys"},
    
    # Galaxy A Series
    {"name": "Samsung Galaxy A54 5G", "brand": "Samsung", "model": "SM-A546B", "device": "a54x", "board": "s5e8835", "fingerprint": "samsung/a54xnaxx/a54x:14/UP1A.231005.007/A546BXXS9CXL1:user/release-keys"},
    {"name": "Samsung Galaxy A34 5G", "brand": "Samsung", "model": "SM-A346B", "device": "a34x", "board": "s5e8835", "fingerprint": "samsung/a34xnaxx/a34x:14/UP1A.231005.007/A346BXXS9CXL1:user/release-keys"},
    {"name": "Samsung Galaxy A14 5G", "brand": "Samsung", "model": "SM-A146B", "device": "a14x", "board": "s5e8535", "fingerprint": "samsung/a14xnaxx/a14x:14/UP1A.231005.007/A146BXXS9CXL1:user/release-keys"},
    
    # Galaxy Z Foldables
    {"name": "Samsung Galaxy Z Fold5", "brand": "Samsung", "model": "SM-F946B", "device": "q5q", "board": "kalama", "fingerprint": "samsung/q5qxxx/q5q:14/UP1A.231005.007/F946BXXS2BXAA:user/release-keys"},
    {"name": "Samsung Galaxy Z Flip5", "brand": "Samsung", "model": "SM-F731B", "device": "b5q", "board": "kalama", "fingerprint": "samsung/b5qxxx/b5q:14/UP1A.231005.007/F731BXXS2BXAA:user/release-keys"},
]

# Xiaomi Devices
XIAOMI_DEVICES = [
    # Xiaomi 14 Series
    {"name": "Xiaomi 14 Pro", "brand": "Xiaomi", "model": "23116PN5BC", "device": "shennong", "board": "pineapple", "fingerprint": "Xiaomi/shennong/shennong:14/UKQ1.231003.002/V816.0.3.0.UNACNXM:user/release-keys"},
    {"name": "Xiaomi 14", "brand": "Xiaomi", "model": "23127PN0CC", "device": "houji", "board": "pineapple", "fingerprint": "Xiaomi/houji/houji:14/UKQ1.231003.002/V816.0.3.0.UNACNXM:user/release-keys"},
    
    # Xiaomi 13 Series
    {"name": "Xiaomi 13 Pro", "brand": "Xiaomi", "model": "2210132G", "device": "nuwa", "board": "kalama", "fingerprint": "Xiaomi/nuwa_global/nuwa:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "Xiaomi 13", "brand": "Xiaomi", "model": "2211133G", "device": "fuxi", "board": "kalama", "fingerprint": "Xiaomi/fuxi_global/fuxi:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "Xiaomi 13T Pro", "brand": "Xiaomi", "model": "23078PND5G", "device": "corot", "board": "mt6985", "fingerprint": "Xiaomi/corot_global/corot:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    
    # Redmi Note Series
    {"name": "Redmi Note 13 Pro+ 5G", "brand": "Xiaomi", "model": "23090RA98G", "device": "zircon", "board": "mt6985", "fingerprint": "Redmi/zircon_global/zircon:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "Redmi Note 13 Pro 5G", "brand": "Xiaomi", "model": "23090PC98G", "device": "sapphire", "board": "mt6985", "fingerprint": "Redmi/sapphire_global/sapphire:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "Redmi Note 13 5G", "brand": "Xiaomi", "model": "23090RA33G", "device": "gold", "board": "mt6985", "fingerprint": "Redmi/gold_global/gold:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "Redmi Note 12 Pro+ 5G", "brand": "Xiaomi", "model": "22101316UG", "device": "ruby", "board": "mt6895", "fingerprint": "Redmi/ruby_global/ruby:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    
    # POCO Series
    {"name": "POCO F5 Pro", "brand": "Xiaomi", "model": "23013PC75G", "device": "mondrian", "board": "kalama", "fingerprint": "POCO/mondrian_global/mondrian:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "POCO F5", "brand": "Xiaomi", "model": "23049PCD8G", "device": "marble", "board": "kalama", "fingerprint": "POCO/marble_global/marble:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
    {"name": "POCO X5 Pro 5G", "brand": "Xiaomi", "model": "22101320G", "device": "redwood", "board": "sm7325", "fingerprint": "POCO/redwood_global/redwood:14/UKQ1.231003.002/V816.0.3.0.UMGMIXM:user/release-keys"},
]

# Google Pixel Devices
PIXEL_DEVICES = [
    # Pixel 8 Series
    {"name": "Google Pixel 8 Pro", "brand": "Google", "model": "Pixel 8 Pro", "device": "husky", "board": "zuma", "fingerprint": "google/husky/husky:14/UD1A.231105.004/11010374:user/release-keys"},
    {"name": "Google Pixel 8", "brand": "Google", "model": "Pixel 8", "device": "shiba", "board": "zuma", "fingerprint": "google/shiba/shiba:14/UD1A.231105.004/11010374:user/release-keys"},
    {"name": "Google Pixel 8a", "brand": "Google", "model": "Pixel 8a", "device": "akita", "board": "zuma", "fingerprint": "google/akita/akita:14/UD1A.231105.004/11010374:user/release-keys"},
    
    # Pixel 7 Series
    {"name": "Google Pixel 7 Pro", "brand": "Google", "model": "Pixel 7 Pro", "device": "cheetah", "board": "gs201", "fingerprint": "google/cheetah/cheetah:14/UP1A.231105.001/11010371:user/release-keys"},
    {"name": "Google Pixel 7", "brand": "Google", "model": "Pixel 7", "device": "panther", "board": "gs201", "fingerprint": "google/panther/panther:14/UP1A.231105.001/11010371:user/release-keys"},
    {"name": "Google Pixel 7a", "brand": "Google", "model": "Pixel 7a", "device": "lynx", "board": "gs201", "fingerprint": "google/lynx/lynx:14/UP1A.231105.001/11010371:user/release-keys"},
    
    # Pixel 6 Series
    {"name": "Google Pixel 6 Pro", "brand": "Google", "model": "Pixel 6 Pro", "device": "raven", "board": "gs101", "fingerprint": "google/raven/raven:14/UP1A.231105.001/11010371:user/release-keys"},
    {"name": "Google Pixel 6", "brand": "Google", "model": "Pixel 6", "device": "oriole", "board": "gs101", "fingerprint": "google/oriole/oriole:14/UP1A.231105.001/11010371:user/release-keys"},
    {"name": "Google Pixel 6a", "brand": "Google", "model": "Pixel 6a", "device": "bluejay", "board": "gs101", "fingerprint": "google/bluejay/bluejay:14/UP1A.231105.001/11010371:user/release-keys"},
]

# OnePlus Devices
ONEPLUS_DEVICES = [
    {"name": "OnePlus 12", "brand": "OnePlus", "model": "CPH2581", "device": "aston", "board": "pineapple", "fingerprint": "OnePlus/CPH2581/OP5961L1:14/UKQ1.231003.002/T.18ca27d_1eec:user/release-keys"},
    {"name": "OnePlus 11 5G", "brand": "OnePlus", "model": "CPH2447", "device": "salami", "board": "kalama", "fingerprint": "OnePlus/CPH2447/OP594FL1:14/UKQ1.231003.002/T.18ca27d_1eec:user/release-keys"},
    {"name": "OnePlus 10 Pro 5G", "brand": "OnePlus", "model": "NE2213", "device": "wukong", "board": "taro", "fingerprint": "OnePlus/NE2213EEA/OP5165L1:14/UKQ1.231003.002/T.18ca27d_1eec:user/release-keys"},
    {"name": "OnePlus Nord 3 5G", "brand": "OnePlus", "model": "CPH2493", "device": "larry", "board": "mt6895", "fingerprint": "OnePlus/CPH2493/OP5A61L1:14/UKQ1.231003.002/T.18ca27d_1eec:user/release-keys"},
    {"name": "OnePlus Nord CE3 5G", "brand": "OnePlus", "model": "CPH2569", "device": "ivan", "board": "sm7325", "fingerprint": "OnePlus/CPH2569/OP5A61L1:14/UKQ1.231003.002/T.18ca27d_1eec:user/release-keys"},
]

# Huawei Devices
HUAWEI_DEVICES = [
    {"name": "Huawei P60 Pro", "brand": "Huawei", "model": "MNA-AL00", "device": "mona", "board": "kirin9000s", "fingerprint": "HUAWEI/MNA-AL00/HWMNA:14/HUAWEIMNA-AL00/100.1.0.178C00:user/release-keys"},
    {"name": "Huawei Mate 60 Pro", "brand": "Huawei", "model": "ALN-AL10", "device": "alan", "board": "kirin9000s", "fingerprint": "HUAWEI/ALN-AL10/HWALN:14/HUAWEIALN-AL10/100.1.0.178C00:user/release-keys"},
    {"name": "Huawei Nova 12 Pro", "brand": "Huawei", "model": "FOA-AL00", "device": "frost", "board": "kirin9000s", "fingerprint": "HUAWEI/FOA-AL00/HWFOA:14/HUAWEIFOA-AL00/100.1.0.178C00:user/release-keys"},
    {"name": "Honor Magic6 Pro", "brand": "Honor", "model": "BVL-AN00", "device": "beverly", "board": "kirin9000s", "fingerprint": "HONOR/BVL-AN00/HWBVL:14/HONORBVL-AN00/100.1.0.178C00:user/release-keys"},
    {"name": "Honor 90", "brand": "Honor", "model": "REA-AN00", "device": "real", "board": "sm7475", "fingerprint": "HONOR/REA-AN00/HWREA:14/HONORREA-AN00/100.1.0.178C00:user/release-keys"},
]

# All devices combined
ALL_DEVICES = {
    "Samsung": SAMSUNG_DEVICES,
    "Xiaomi": XIAOMI_DEVICES,
    "Google": PIXEL_DEVICES,
    "OnePlus": ONEPLUS_DEVICES,
    "Huawei": HUAWEI_DEVICES,
}


def get_all_models():
    """Get all available device models grouped by brand"""
    return ALL_DEVICES


def get_model_profile(model_name):
    """Get profile for a specific model by name"""
    for brand_devices in ALL_DEVICES.values():
        for device in brand_devices:
            if device["name"].lower() == model_name.lower():
                return device
            # Also match by partial name
            if model_name.lower() in device["name"].lower():
                return device
    return None


def get_models_by_brand(brand):
    """Get all models for a specific brand"""
    brand = brand.capitalize()
    return ALL_DEVICES.get(brand, [])


def search_models(query):
    """Search models by name"""
    query = query.lower()
    results = []
    for brand_devices in ALL_DEVICES.values():
        for device in brand_devices:
            if query in device["name"].lower() or query in device["model"].lower():
                results.append(device)
    return results
