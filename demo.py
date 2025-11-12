#!/usr/bin/env python3
"""
Demo script to show how to use the Ingot server and configuration.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingot.ingot import IngotConfig, IngotServer, create_server


def demo_configuration():
    """Demonstrate different configuration options."""
    print("=== Configuration Demo ===")
    
    # 1. Basic configuration
    print("\n1. Basic configuration:")
    config1 = IngotConfig(upload_root="/tmp/ingot-demo")
    print(f"   Upload root: {config1.upload_root}")
    print(f"   Max file size: {config1.max_file_size:,} bytes")
    print(f"   Create dirs: {config1.create_dirs}")
    
    # 2. Custom configuration
    print("\n2. Custom configuration:")
    config2 = IngotConfig(
        upload_root="/tmp/custom-ingot",
        max_file_size=50 * 1024 * 1024,  # 50MB
        create_dirs=True
    )
    print(f"   Upload root: {config2.upload_root}")
    print(f"   Max file size: {config2.max_file_size:,} bytes")
    
    # 3. Configuration from environment
    print("\n3. Configuration from environment:")
    import os
    os.environ["INGOT_UPLOAD_ROOT"] = "/tmp/env-ingot"
    os.environ["INGOT_MAX_FILE_SIZE"] = "209715200"  # 200MB
    
    config3 = IngotConfig.from_env()
    print(f"   Upload root: {config3.upload_root}")
    print(f"   Max file size: {config3.max_file_size:,} bytes")
    
    # Clean up
    os.environ.pop("INGOT_UPLOAD_ROOT", None)
    os.environ.pop("INGOT_MAX_FILE_SIZE", None)


def demo_server_creation():
    """Demonstrate server creation with different configurations."""
    print("\n=== Server Creation Demo ===")
    
    # 1. Server with default config
    print("\n1. Server with default configuration:")
    server1 = create_server()
    print(f"   Upload root: {server1.config.upload_root}")
    print(f"   Number of routes: {len(server1.app.routes)}")
    
    # 2. Server with custom upload root
    print("\n2. Server with custom upload root:")
    server2 = create_server("/tmp/demo-uploads")
    print(f"   Upload root: {server2.config.upload_root}")
    
    # 3. Server with full custom config
    print("\n3. Server with custom configuration:")
    custom_config = IngotConfig(
        upload_root="/tmp/fully-custom",
        max_file_size=10 * 1024 * 1024,  # 10MB
        create_dirs=True
    )
    server3 = IngotServer(custom_config)
    print(f"   Upload root: {server3.config.upload_root}")
    print(f"   Max file size: {server3.config.max_file_size:,} bytes")


def demo_routes():
    """Show available routes in the server."""
    print("\n=== Available Routes ===")
    
    server = create_server()
    
    print("\nAPI Endpoints:")
    for route in server.app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = list(route.methods)
            print(f"   {methods[0]:<6} {route.path}")


def main():
    """Run all demos."""
    print("Ingot Server Configuration and Setup Demo")
    print("=" * 50)
    
    demo_configuration()
    demo_server_creation()
    demo_routes()
    
    print("\n" + "=" * 50)
    print("Demo complete!")
    print("\nTo start the server, run:")
    print("  python -m src.ingot.ingot --serve")
    print("  python -m src.ingot.ingot --serve --upload-root /custom/path")
    print("  python -m src.ingot.ingot --serve --host 0.0.0.0 --port 8080")


if __name__ == "__main__":
    main()