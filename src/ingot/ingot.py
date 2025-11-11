from argparse import ArgumentParser
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

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

    