"""
Pytest tests for Ingot upload endpoint.
"""

import sys
import tempfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingot.ingot import IngotConfig, IngotServer


@pytest.fixture
def temp_config():
    """Create a temporary configuration for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = IngotConfig(
            upload_root=temp_dir,
            max_file_size=1024 * 1024,  # 1MB
            create_dirs=True
        )
        yield config


@pytest.fixture
def server(temp_config):
    """Create a server instance with temporary configuration."""
    return IngotServer(temp_config)


@pytest.fixture
def client(server):
    """Create a test client."""
    return TestClient(server.app)


def test_upload_simple_file(client, temp_config):
    """Test uploading a simple text file."""
    test_content = b"Hello, World!"
    test_filename = "hello.txt"
    
    response = client.post(
        "/upload/test-repo/docs",
        files={"file": (test_filename, test_content, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["filename"] == test_filename
    assert data["repository"] == "test-repo"
    assert data["size"] == len(test_content)
    assert "test-repo/docs/hello.txt" in data["path"]
    
    # Verify file exists on disk
    expected_path = Path(temp_config.upload_root) / "test-repo" / "docs" / test_filename
    assert expected_path.exists()
    assert expected_path.read_bytes() == test_content


def test_upload_without_path(client, temp_config):
    """Test uploading a file without specifying a path."""
    test_content = b"Root level file"
    test_filename = "root.txt"
    
    response = client.post(
        "/upload/my-repo/",
        files={"file": (test_filename, test_content, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify file is in repository root
    expected_path = Path(temp_config.upload_root) / "my-repo" / test_filename
    assert expected_path.exists()
    assert expected_path.read_bytes() == test_content


def test_upload_missing_repository(client):
    """Test upload fails when repository name is missing."""
    response = client.post(
        "/upload//test.txt",
        files={"file": ("test.txt", b"content", "text/plain")}
    )
    
    # FastAPI should handle this as a 404 since the route won't match
    assert response.status_code == 404


def test_upload_creates_nested_directories(client, temp_config):
    """Test that nested directories are created automatically."""
    test_content = b"Nested file content"
    test_filename = "nested.txt"
    
    response = client.post(
        "/upload/repo/very/deep/nested/path",
        files={"file": (test_filename, test_content, "text/plain")}
    )
    
    assert response.status_code == 200
    
    # Verify nested directory structure was created
    expected_path = Path(temp_config.upload_root) / "repo" / "very" / "deep" / "nested" / "path" / test_filename
    assert expected_path.exists()
    assert expected_path.read_bytes() == test_content


def test_upload_different_file_types(client, temp_config):
    """Test uploading different file types."""
    test_files = [
        ("document.txt", b"Text content", "text/plain"),
        ("data.json", b'{"key": "value"}', "application/json"),
        ("binary.bin", b"\x00\x01\x02\x03", "application/octet-stream"),
        ("image.png", b"\x89PNG\r\n\x1a\n", "image/png")
    ]
    
    for filename, content, content_type in test_files:
        response = client.post(
            "/upload/files/mixed",
            files={"file": (filename, content, content_type)}
        )
        
        assert response.status_code == 200, f"Failed to upload {filename}"
        
        # Verify file exists
        expected_path = Path(temp_config.upload_root) / "files" / "mixed" / filename
        assert expected_path.exists()
        assert expected_path.read_bytes() == content


def test_configuration_from_env():
    """Test creating configuration from environment variables."""
    import os
    
    # Set environment variables
    test_root = "/tmp/test-ingot"
    test_size = "2097152"  # 2MB
    
    os.environ["INGOT_UPLOAD_ROOT"] = test_root
    os.environ["INGOT_MAX_FILE_SIZE"] = test_size
    
    try:
        config = IngotConfig.from_env()
        assert str(config.upload_root) == test_root
        assert config.max_file_size == int(test_size)
    finally:
        # Clean up environment variables
        os.environ.pop("INGOT_UPLOAD_ROOT", None)
        os.environ.pop("INGOT_MAX_FILE_SIZE", None)


def test_config_creates_upload_directory():
    """Test that configuration creates the upload directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        upload_path = Path(temp_dir) / "ingot-uploads"
        
        config = IngotConfig(upload_root=upload_path, create_dirs=True)
        
        assert upload_path.exists()
        assert upload_path.is_dir()


@pytest.mark.asyncio
async def test_server_endpoints_exist(server):
    """Test that all expected endpoints are available."""
    routes = [route.path for route in server.app.routes]
    
    expected_routes = [
        "/upload/{repository_name}/{path:path}",
        "/download/{file_id}",
        "/list",
        "/delete/{file_id}"
    ]
    
    for expected_route in expected_routes:
        assert expected_route in routes