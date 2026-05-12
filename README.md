# ai-code-starter
This project is an AI-powered smart developer assistant tool that converts business requirements (BRD, Jira, test cases) into a runnable Spring Boot project.

## Features

- **AI-Powered Analysis**: Uses OpenRouter API with advanced language models to analyze business requirements
- **MCP Integration**: Enhanced with Model Context Protocol server providing Spring Boot best practices and validation
- **Automated Code Generation**: Generates complete Spring Boot projects with entities, repositories, services, and controllers
- **REST API**: FastAPI-based web service for easy integration
- **Template-Based Generation**: Uses Jinja2 templates for consistent code structure

## MCP (Model Context Protocol) Integration

The system includes MCP server integration that provides:

### Available MCP Tools

1. **Spring Boot Context** (`get_spring_boot_context`)
   - Provides contextual information based on requirements
   - Includes best practices for entities, repositories, services, and controllers
   - Adapts context based on detected patterns (users, products, etc.)

2. **Entity Validation** (`validate_entity_design`)
   - Validates entity structures against Spring Boot best practices
   - Provides suggestions for improvements
   - Checks for required fields and proper naming

3. **API Best Practices** (`get_api_best_practices`)
   - REST API design guidelines
   - HTTP status codes and response formats
   - Error handling recommendations

4. **Project Structure** (`generate_code_structure`)
   - Recommended Spring Boot project layout
   - Dependency suggestions
   - File organization best practices

### MCP API Endpoints

- `POST /mcp/context` - Get Spring Boot context for requirements
- `POST /mcp/validate-entity` - Validate entity design
- `GET /mcp/api-practices` - Get API best practices
- `POST /mcp/project-structure` - Generate project structure

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenRouter API key in `tools/analyzer.py`
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## Usage

1. Start the FastAPI server
2. Upload a requirements file via `POST /generate`
3. The system will:
   - Parse the requirements
   - Analyze with AI + MCP context
   - Validate entity designs
   - Generate Spring Boot code
   - Return a ZIP file with the complete project

## Architecture

- `main.py` - FastAPI web server with MCP endpoints
- `orchestrator.py` - Pipeline orchestration
- `tools/analyzer.py` - AI analysis with MCP integration
- `tools/parser.py` - File parsing utilities
- `tools/generator.py` - Code generation engine
- `tools/mcp_server.py` - MCP server implementation
- `templates/` - Jinja2 code templates
- `models/` - Data models and schemas
