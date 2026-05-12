from fastapi import FastAPI, UploadFile, HTTPException
import os
from orchestrator import run_pipeline
from tools.mcp_server import get_spring_boot_context, validate_entity_design, get_api_best_practices, generate_code_structure

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

@app.post("/mcp/context")
async def get_mcp_context(requirements: str):
    """Get Spring Boot context for requirements analysis"""
    try:
        context = get_spring_boot_context(requirements)
        return {"context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP context error: {str(e)}")

@app.post("/mcp/validate-entity")
async def validate_entity(entity_data: dict):
    """Validate entity design against Spring Boot best practices"""
    try:
        validation = validate_entity_design(entity_data)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entity validation error: {str(e)}")

@app.get("/mcp/api-practices")
async def get_api_practices():
    """Get REST API best practices for Spring Boot"""
    try:
        practices = get_api_best_practices()
        return {"practices": practices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API practices error: {str(e)}")

@app.post("/mcp/project-structure")
async def get_project_structure(project_name: str):
    """Generate recommended Spring Boot project structure"""
    try:
        structure = generate_code_structure(project_name)
        return structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project structure error: {str(e)}")