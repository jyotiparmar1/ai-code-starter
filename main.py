from fastapi import FastAPI, UploadFile, HTTPException, Form, File
from fastapi.responses import FileResponse
from typing import Optional
import os
from orchestrator import get_orchestrator
from pydantic import BaseModel


class MCPContextRequest(BaseModel):
    requirements: str


class ProjectStructureRequest(BaseModel):
    project_name: str


class PipelineRequest(BaseModel):
    file_path: str
    project_name: str = "generated-project"


app = FastAPI()

# Get the MCP orchestrator
orchestrator = get_orchestrator()


@app.post("/generate")
async def generate(file: UploadFile):
    """Generate a Spring Boot project from an uploaded PRD file"""
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_path = f"temp_{file.filename}"
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # Extract project name from filename if possible, otherwise use default
        project_name = os.path.splitext(file.filename)[0].replace("-", "_")
        
        # Run the MCP pipeline through the orchestrator
        zip_path = await orchestrator.run_pipeline_async(file_path, project_name)
        
        return {
            "success": True,
            "zip_file": zip_path,
            "message": f"Project generated successfully: {zip_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/pipeline")
async def run_pipeline_endpoint(request: PipelineRequest):
    """Run the MCP pipeline with a file path and project name"""
    try:
        if not os.path.exists(request.file_path):
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {request.file_path}"
            )
        
        zip_path = await orchestrator.run_pipeline_async(request.file_path, request.project_name)
        
        return {
            "success": True,
            "zip_file": zip_path,
            "message": f"Pipeline executed successfully: {zip_path}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )


@app.post("/mcp/context")
async def mcp_context(request: MCPContextRequest):
    try:
        context = (await orchestrator.mcp_server.call_tool_async("get_spring_boot_context", requirements=request.requirements))["result"]
        return {
            "success": True,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve MCP context: {str(e)}")


@app.post("/mcp/project-structure")
async def project_structure(request: ProjectStructureRequest):
    try:
        structure = await orchestrator.mcp_server.call_tool_async("get_project_structure", project_name=request.project_name)
        return {
            "success": True,
            "structure": structure
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not generate project structure: {str(e)}")


@app.post("/mcp/validate-database")
async def validate_database(request: dict):
    """Validate database schema"""
    try:
        validation = orchestrator.mcp_server.call_tool("validate_database_schema", entities=request)
        return {
            "success": True,
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not validate database schema: {str(e)}")


@app.post("/generate/jira")
async def generate_from_jira(
    issue_keys: str = Form(...),
    project_name: str = Form("generated-project"),
    jira_url: Optional[str] = Form(None),
    jira_email: Optional[str] = Form(None),
    jira_token: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """Generate a Spring Boot project from one or more JIRA issues (comma-separated keys)."""
    prd_file_path = None
    try:
        parsed_keys = [k.strip() for k in issue_keys.split(",") if k.strip()]
        if not parsed_keys:
            raise HTTPException(status_code=400, detail="No valid JIRA issue keys provided.")

        if file:
            contents = await file.read()
            if contents:
                prd_file_path = f"temp_jira_{file.filename}"
                with open(prd_file_path, "wb") as f:
                    f.write(contents)

        zip_path = await orchestrator.run_pipeline_with_jira_async(
            jira_issue_keys=parsed_keys,
            project_name=project_name,
            prd_file_path=prd_file_path,
            jira_url=jira_url or None,
            jira_email=jira_email or None,
            jira_token=jira_token or None,
        )

        return {
            "success": True,
            "zip_file": zip_path,
            "issue_keys": parsed_keys,
            "message": f"Project generated from {len(parsed_keys)} JIRA issue(s): {', '.join(parsed_keys)}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JIRA generation failed: {str(e)}")
    finally:
        if prd_file_path and os.path.exists(prd_file_path):
            os.remove(prd_file_path)


@app.get("/download")
async def download_zip():
    """Serve the most recently generated project zip."""
    zip_path = "output/project.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="No generated project found.")
    return FileResponse(zip_path, filename="generated_spring_boot_app.zip", media_type="application/zip")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCP Code Generation Pipeline"
    }