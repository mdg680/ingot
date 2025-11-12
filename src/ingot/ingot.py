import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from fastapi import FastAPI, File, UploadFile, HTTPException


@dataclass
class IngotConfig:
    """Configuration class for Ingot storage server."""
    upload_root: Path
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
    allowed_extensions: Optional[set] = None
    create_dirs: bool = True
    
    def __post_init__(self):
        """Ensure upload_root is a Path object and create it if needed."""
        self.upload_root = Path(self.upload_root)
        if self.create_dirs:
            self.upload_root.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "IngotConfig":
        """Create configuration from environment variables."""
        upload_root = os.getenv("INGOT_UPLOAD_ROOT", "/tmp/ingot-uploads")
        max_file_size = int(os.getenv("INGOT_MAX_FILE_SIZE", 100 * 1024 * 1024))
        return cls(upload_root=upload_root, max_file_size=max_file_size)


class IngotServer:
    """Ingot storage server with configurable endpoints."""
    
    def __init__(self, config: IngotConfig):
        self.config = config
        self.app = FastAPI(title="Ingot Storage Server")
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        self.app.post("/upload/{repository_name}/{path:path}")(self.upload_file)
        self.app.get("/download/{file_id}")(self.download_file)
        self.app.get("/list")(self.list_files)
        self.app.delete("/delete/{file_id}")(self.delete_file)
    
    async def upload_file(self, file: UploadFile = File(...), repository_name: str = None, path: str = None):
        """Upload a file to the storage server."""
        if not repository_name:
            raise HTTPException(status_code=400, detail="Repository name is required")
        
        # Check file size
        if hasattr(file, 'size') and file.size and file.size > self.config.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {self.config.max_file_size} bytes"
            )
        
        try:
            # Build destination path
            repo_path = self.config.upload_root / repository_name
            if path:
                destination_dir = repo_path / path
            else:
                destination_dir = repo_path
            
            # Create directory if it doesn't exist
            destination_dir.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            destination_file = destination_dir / file.filename
            
            # TODO: do multipart uploads properly
            contents = await file.read()
            
            # Write file to destination
            with open(destination_file, "wb") as f:
                f.write(contents)
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        finally:
            await file.close()
            
        return {
            "filename": file.filename,
            "repository": repository_name,
            "path": str(destination_file.relative_to(self.config.upload_root)),
            "size": len(contents) if 'contents' in locals() else 0
        }
    
    async def download_file(self, file_id: str):
        """Download a file from the storage server."""
        # TODO: Implement file download logic
        return {"file_id": file_id, "status": "not implemented"}
    
    async def list_files(self):
        """List all files in the storage server."""
        # TODO: Implement file listing logic
        return {"files": [], "status": "not implemented"}
    
    async def delete_file(self, file_id: str):
        """Delete a file from the storage server."""
        # TODO: Implement file deletion logic
        return {"file_id": file_id, "status": "not implemented"}


def parse_args():
    parser = ArgumentParser(description="Ingot CLI")
    parser.add_argument("--upload", "-u", type=str, help="Upload a file")
    parser.add_argument("--download", "-d", type=str, help="Download a file")
    parser.add_argument("--list", "-l", action="store_true", help="List files")
    parser.add_argument("--delete", "-r", type=str, help="Delete a file")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")
    parser.add_argument("--upload-root", type=str, help="Override upload root directory")
    parser.add_argument("--serve", "-s", action="store_true", help="Start the server")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")

    return parser.parse_args()


def create_server(upload_root: Optional[str] = None) -> IngotServer:
    """Create and configure the Ingot server."""
    if upload_root:
        config = IngotConfig(upload_root=upload_root)
    else:
        config = IngotConfig.from_env()
    
    return IngotServer(config)


if __name__ == "__main__":
    args = parse_args()
    
    if args.serve:
        import uvicorn
        server = create_server(args.upload_root)
        print(f"Starting Ingot server on {args.host}:{args.port}")
        print(f"Upload root: {server.config.upload_root}")
        uvicorn.run(server.app, host=args.host, port=args.port)
    else:
        # TODO: Implement CLI operations
        print("CLI operations not implemented yet")

    