from fastapi import FastAPI, UploadFile, HTTPException
import os
from orchestrator import get_orchestrator
from pydantic import BaseModel


class ProjectNameRequest(BaseModel):
    project_name: str


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
        zip_path = orchestrator.run_pipeline(file_path, project_name)
        
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
        
        zip_path = orchestrator.run_pipeline(request.file_path, request.project_name)
        
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


@app.get("/mcp/tools")
async def get_mcp_tools():
    """Get information about available MCP tools"""
    try:
        tools_info = orchestrator.get_tool_info()
        return {
            "success": True,
            "tools": tools_info,
            "count": len(tools_info)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve tools: {str(e)}"
        )


@app.get("/mcp/api-practices")
async def api_best_practices():
    try:
        practices = orchestrator.mcp_server.call_tool("get_api_best_practices")
        return {
            "success": True,
            "practices": practices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve API best practices: {str(e)}")


@app.post("/mcp/context")
async def mcp_context(request: MCPContextRequest):
    try:
        context = orchestrator.mcp_server.call_tool("get_spring_boot_context", requirements=request.requirements)
        return {
            "success": True,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve MCP context: {str(e)}")


@app.post("/mcp/project-structure")
async def project_structure(request: ProjectStructureRequest):
    try:
        structure = orchestrator.mcp_server.call_tool("get_project_structure", project_name=request.project_name)
        return {
            "success": True,
            "structure": structure
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not generate project structure: {str(e)}")


@app.post("/mcp/validate-entity")
async def validate_entity(request: dict):
    """Validate entity design"""
    try:
        validation = orchestrator.mcp_server.call_tool("validate_entity_design", entity_data=request)
        return {
            "success": True,
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not validate entity: {str(e)}")


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


@app.post("/mcp/suggest-dependencies")
async def suggest_dependencies_endpoint(request: dict):
    """Suggest Maven dependencies"""
    try:
        suggestions = orchestrator.mcp_server.call_tool("suggest_dependencies", features=request)
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not suggest dependencies: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCP Code Generation Pipeline"
    }