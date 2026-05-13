from fastapi import FastAPI, UploadFile
import shutil
import os
from orchestrator import run_pipeline

app = FastAPI()

@app.post("/generate")
async def generate(file: UploadFile):
    file_path = f"temp_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        zip_path = run_pipeline(file_path)
        return {"zip_file": zip_path}
    finally:
        try:
            os.remove(file_path)
        except OSError:
            pass