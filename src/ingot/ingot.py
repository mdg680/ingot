from argparse import ArgumentParser
from fastapi import FastAPI, File, Path, UploadFile, HTTPException

app = FastAPI()

@app.post("/upload/{repository_name}/{path:path}")
async def upload_file(file: UploadFile = File(...), repository_name: str = None, path: str = None):
    if not repository_name:
        raise HTTPException(status_code=400, detail="Repository name is required")
    try:
        # TODO: do multipart uploads properly
        contents = await file.read()
        # Here you would normally save the file to the destination
        destination = f"/{repository_name}/{path or ''}"
        with open(destination / file.filename, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await file.close()
    return {
        "Successfully uploaded filename": file.filename, 
        "to destination destination": str(destination)
    }

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    return {"file_id": file_id}

@app.get("/list")
async def list_files():
    return {"files": []}

@app.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    return {"file_id": file_id}

def parse_args():
    parser = ArgumentParser(description="Ingot CLI")
    parser.add_argument("--upload", "-u", type=str, help="Upload a file")
    parser.add_argument("--download", "-d", type=str, help="Download a file")
    parser.add_argument("--list", "-l", action="store_true", help="List files")
    parser.add_argument("--delete", "-r", type=str, help="Delete a file")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    