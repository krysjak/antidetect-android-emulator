"""
AntiDetect Android Emulator - Main Entry Point
"""
import click
import webbrowser
from colorama import init, Fore, Style

init()  # Initialize colorama

@click.group()
@click.version_option(version="1.0.0", prog_name="AntiDetect Emulator")
def cli():
    """🤖 AntiDetect Android Emulator - Anonymous phone emulation"""
    pass


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind")
@click.option("--port", default=8080, help="Port to bind")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
def gui(host, port, no_browser):
    """Start the web GUI dashboard"""
    from gui.app import create_app, socketio
    
    print(f"{Fore.CYAN}🤖 AntiDetect Emulator{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Starting GUI on http://{host}:{port}{Style.RESET_ALL}")
    
    if not no_browser:
        webbrowser.open(f"http://{host}:{port}")
    
    app = create_app()
    socketio.run(app, host=host, port=port, debug=False)


@cli.command("list")
def list_devices():
    """List all created devices"""
    from core.device_manager import DeviceManager
    
    manager = DeviceManager()
    devices = manager.list_devices()
    
    if not devices:
        print(f"{Fore.YELLOW}No devices found. Create one with 'create' command.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}📱 Your Devices:{Style.RESET_ALL}\n")
    for device in devices:
        status = f"{Fore.GREEN}● Running{Style.RESET_ALL}" if device.get("running") else f"{Fore.RED}○ Stopped{Style.RESET_ALL}"
        print(f"  {device['name']}")
        print(f"    Model: {device['model']}")
        print(f"    Android: {device['android_version']}")
        print(f"    Status: {status}")
        print()


@cli.command()
@click.option("--model", "-m", required=True, help="Phone model (e.g., 'Samsung Galaxy S24')")
@click.option("--android", "-a", default="14", help="Android version (9-14)")
@click.option("--name", "-n", help="Device name (auto-generated if not specified)")
@click.option("--proxy", "-p", help="Proxy address (e.g., socks5://127.0.0.1:1080)")
def create(model, android, name, proxy):
    """Create a new emulator device"""
    from core.device_manager import DeviceManager
    
    manager = DeviceManager()
    
    try:
        device = manager.create_device(
            model=model,
            android_version=android,
            name=name,
            proxy=proxy
        )
        print(f"{Fore.GREEN}✓ Device created: {device['name']}{Style.RESET_ALL}")
        print(f"  Model: {device['model']}")
        print(f"  Android: {device['android_version']}")
        if proxy:
            print(f"  Proxy: {proxy}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


@cli.command()
@click.argument("name")
@click.option("--frida", is_flag=True, help="Enable Frida hooks")
def launch(name, frida):
    """Launch a device by name"""
    from core.device_manager import DeviceManager
    
    manager = DeviceManager()
    
    print(f"{Fore.CYAN}🚀 Launching {name}...{Style.RESET_ALL}")
    
    try:
        manager.launch_device(name, enable_frida=frida)
        print(f"{Fore.GREEN}✓ Device launched successfully{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


@cli.command()
@click.argument("name")
def stop(name):
    """Stop a running device"""
    from core.device_manager import DeviceManager
    
    manager = DeviceManager()
    
    try:
        manager.stop_device(name)
        print(f"{Fore.GREEN}✓ Device stopped{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")


@cli.command()
def models():
    """List available phone models"""
    from profiles.device_profiles import get_all_models
    
    models = get_all_models()
    
    print(f"\n{Fore.CYAN}📱 Available Phone Models:{Style.RESET_ALL}\n")
    
    for brand, brand_models in models.items():
        print(f"{Fore.YELLOW}{brand}:{Style.RESET_ALL}")
        for model in brand_models[:5]:  # Show first 5
            print(f"  • {model['name']}")
        if len(brand_models) > 5:
            print(f"  ... and {len(brand_models) - 5} more")
        print()


@cli.command()
def check_sdk():
    """Check Android SDK installation"""
    import config
    import os
    
    print(f"\n{Fore.CYAN}🔍 Checking Android SDK...{Style.RESET_ALL}\n")
    
    if config.ANDROID_SDK_ROOT:
        print(f"{Fore.GREEN}✓ ANDROID_SDK_ROOT: {config.ANDROID_SDK_ROOT}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ ANDROID_SDK_ROOT not set{Style.RESET_ALL}")
    
    # Check emulator
    if os.path.exists(config.EMULATOR_PATH):
        print(f"{Fore.GREEN}✓ Emulator found{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Emulator not found at {config.EMULATOR_PATH}{Style.RESET_ALL}")
    
    # Check ADB
    if os.path.exists(config.ADB_PATH):
        print(f"{Fore.GREEN}✓ ADB found{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ ADB not found at {config.ADB_PATH}{Style.RESET_ALL}")


if __name__ == "__main__":
    cli()
