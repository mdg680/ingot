#!/usr/bin/env python3
"""
Simple test script for the Ingot upload endpoint.
This demonstrates how to test the upload functionality.
"""

import sys
import tempfile
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ingot.ingot import IngotConfig, IngotServer


def test_upload_endpoint():
    """Test the upload endpoint with a temporary file."""
    
    # Create a temporary directory for uploads
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create configuration with temporary upload root
        config = IngotConfig(
            upload_root=temp_dir,
            max_file_size=1024 * 1024  # 1MB for testing
        )
        
        # Create server instance
        server = IngotServer(config)
        
        # Create test client
        client = TestClient(server.app)
        
        # Create a test file
        test_content = b"Hello, this is a test file!"
        test_filename = "test.txt"
        
        # Test upload
        response = client.post(
            "/upload/my-repo/subdir",
            files={"file": (test_filename, test_content, "text/plain")}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.json()}")
        
        # Verify the file was created
        expected_path = Path(temp_dir) / "my-repo" / "subdir" / test_filename
        if expected_path.exists():
            print(f"\033[32m[PASS]\033[0m File successfully created at: {expected_path}")
            with open(expected_path, 'rb') as f:
                saved_content = f.read()
                if saved_content == test_content:
                    print("\033[32m[PASS]\033[0m File content matches!")
                else:
                    print("\033[31m[FAIL]\033[0m File content doesn't match!")
        else:
            print(f"\033[31m[FAIL]\033[0m File not found at: {expected_path}")


def test_upload_with_custom_config():
    """Test upload with custom configuration."""
    
    # Create a custom upload directory
    upload_dir = Path("/tmp/ingot-test-uploads")
    
    config = IngotConfig(
        upload_root=upload_dir,
        max_file_size=500 * 1024,  # 500KB
        create_dirs=True
    )
    
    server = IngotServer(config)
    client = TestClient(server.app)
    
    # Test with different file types
    test_files = [
        ("document.txt", b"Text document content", "text/plain"),
        ("data.json", b'{"key": "value"}', "application/json"),
        ("image.bin", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", "application/octet-stream")
    ]
    
    for filename, content, content_type in test_files:
        response = client.post(
            f"/upload/test-repo/files",
            files={"file": (filename, content, content_type)}
        )
        
        print(f"Upload {filename}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Path: {data.get('path')}")
            print(f"  Size: {data.get('size')} bytes")
        else:
            print(f"  Error: {response.json()}")
    
    print(f"\nFiles in upload directory:")
    if upload_dir.exists():
        for file_path in upload_dir.rglob("*"):
            if file_path.is_file():
                print(f"  {file_path.relative_to(upload_dir)} ({file_path.stat().st_size} bytes)")


if __name__ == "__main__":
    print("Testing Ingot upload endpoint...")
    print("=" * 50)
    
    print("\n1. Basic upload test:")
    test_upload_endpoint()
    
    print("\n2. Custom configuration test:")
    test_upload_with_custom_config()
    
    print("\n" + "=" * 50)
    print("Testing complete!")