from fastapi import FastAPI, UploadFile, HTTPException
import os
from orchestrator import run_pipeline

app = FastAPI()

@app.post("/generate")
async def generate(file: UploadFile):
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_path = f"temp_{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        zip_path = run_pipeline(file_path)
        return {"zip_file": zip_path}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)