# MCP Orchestration Layer Architecture

## Overview

The application now uses **MCP (Model Context Protocol) as an orchestration layer** where each tool (parser, analyzer, generator) is wrapped as an MCP tool. The architecture follows a **client-server model** where:

- **MCP Server** (`tools/mcp_server.py`): Exposes parser, analyzer, and generator as MCP tools
- **MCP Client/Orchestrator** (`orchestrator.py`): Calls the MCP server tools to orchestrate the pipeline
- **FastAPI Entry Point** (`main.py`): Receives requests and delegates to the orchestrator

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI (main.py)                       │
│  • POST /generate - Upload PRD and generate project             │
│  • POST /pipeline - Run pipeline with file path                 │
│  • GET  /mcp/tools - Get available MCP tools                    │
│  • GET  /health - Health check                                  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│            MCPOrchestrator (orchestrator.py)                     │
│  • MCP Client that manages the pipeline workflow                │
│  • Calls MCP server tools in sequence                           │
│  • Error handling and logging                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              MCPServer (tools/mcp_server.py)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Tool: parse_prd                                          │  │
│  │ Wraps: tools/parser.py                                   │  │
│  │ Input: file_path                                         │  │
│  │ Output: {content, length, success}                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Tool: analyze_prd                                        │  │
│  │ Wraps: tools/analyzer.py                                 │  │
│  │ Input: prd_text, project_name                            │  │
│  │ Output: {analysis: {...}, success}                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Tool: generate_project                                   │  │
│  │ Wraps: tools/generator.py                                │  │
│  │ Input: analysis_data                                     │  │
│  │ Output: {zip_path, success}                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Pipeline Workflow

### Step 1: Parse PRD
```
POST /generate (upload PRD file)
    ↓
main.py: extract filename, save temp file
    ↓
orchestrator.run_pipeline(file_path, project_name)
    ↓
mcp_server.parse_prd(file_path)
    ↓
tools/parser.py: parse(file_path) → raw text
    ↓
Return: {success: true, content: "...", length: N}
```

### Step 2: Analyze PRD
```
orchestrator receives parsed content
    ↓
mcp_server.analyze_prd(prd_text, project_name)
    ↓
tools/analyzer.py: analyze(prd_text, project_name)
    ↓
OpenRouter API → extract entities, fields, CRUD operations
    ↓
Return: {success: true, analysis: {...}}
```

### Step 3: Generate Project
```
orchestrator receives analysis data
    ↓
mcp_server.generate_project(analysis_data)
    ↓
tools/generator.py: generate(analysis_data)
    ↓
Infer features → Render Jinja2 templates → Create ZIP
    ↓
Return: {success: true, zip_path: "output/project.zip"}
```

## API Endpoints

### 1. **POST /generate** - Upload and Generate
```bash
curl -X POST -F "file=@sample.docx" http://localhost:8000/generate
```

**Response:**
```json
{
  "success": true,
  "zip_file": "output/project.zip",
  "message": "Project generated successfully: output/project.zip"
}
```

### 2. **POST /pipeline** - Direct Pipeline Execution
```bash
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"file_path": "sample_prd.md", "project_name": "my_project"}'
```

**Response:**
```json
{
  "success": true,
  "zip_file": "output/project.zip",
  "message": "Pipeline executed successfully: output/project.zip"
}
```

### 3. **GET /mcp/tools** - List Available Tools
```bash
curl http://localhost:8000/mcp/tools
```

**Response:**
```json
{
  "success": true,
  "tools": {
    "parse_prd": {
      "description": "Parse a PRD file...",
      "inputSchema": {...}
    },
    "analyze_prd": {...},
    "generate_project": {...}
  },
  "count": 3
}
```

### 4. **GET /health** - Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "MCP Code Generation Pipeline"
}
```

## Key Components

### MCPServer (tools/mcp_server.py)
- Exposes three MCP tools: `parse_prd`, `analyze_prd`, `generate_project`
- Each tool wraps an existing module
- Provides standardized input/output schemas
- Handles errors and returns success/failure status

### MCPOrchestrator (orchestrator.py)
- Acts as an MCP **client**
- Orchestrates the 3-step pipeline
- Calls tools in sequence
- Provides logging and error handling
- Exposes `get_orchestrator()` singleton for easy access

### Tools (Existing Modules - Unchanged)
- `tools/parser.py`: Parses PRD files (docx, md, txt)
- `tools/analyzer.py`: Analyzes PRD with OpenRouter API
- `tools/generator.py`: Generates Spring Boot project

## Benefits of This Architecture

1. **Clear Separation of Concerns**: MCP is purely orchestration/tool exposure
2. **Extensible**: Easy to add new tools without changing core orchestration
3. **Standardized Interfaces**: Each tool has a consistent schema
4. **Client-Server Model**: Tools are decoupled from FastAPI
5. **Backward Compatible**: Existing `/generate` endpoint still works
6. **Tool Discovery**: `/mcp/tools` endpoint lists all available tools





## Future Enhancements

### Multi-Tool Extension
Each tool could become a separate MCP server:
```
Parser MCP Server  ─────┐
                        ├─→ Main Orchestrator ──→ FastAPI
Analyzer MCP Server ────┤
                        ├─→
Generator MCP Server ───┘
```

### Advanced Features
- Tool chaining and composition
- Conditional branching based on analysis results
- Tool caching and optimization
- Parallel tool execution for independent operations
- Custom tool registration
- Tool versioning

## Running the Application

```bash
# Start the application
python main.py

# Or with uvicorn explicitly
uvicorn main:app --reload --port 8000
```

The FastAPI server will start and the MCP orchestrator will be ready to handle requests.

## Testing the Pipeline

```bash
# Test with sample PRD
curl -X POST -F "file=@sample_prd.md" http://localhost:8000/generate

# Check available tools
curl http://localhost:8000/mcp/tools

# Health check
curl http://localhost:8000/health
```
