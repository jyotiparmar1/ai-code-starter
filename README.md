# ai-code-starter

AI-powered code generator that converts PRD documents into complete, runnable Spring Boot projects.

## 🚀 Quick Start

### Option 1: One-Click Start (Recommended)

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

This will automatically:
- Install all dependencies
- Start the FastAPI backend on http://localhost:8000
- Launch the Streamlit UI on http://localhost:8501

### Option 2: Manual Setup

```bash
# Create virtual environment (optional but recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn main:app --reload &

# Start the Streamlit UI (in another terminal)
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

## 🎨 Streamlit UI Features

The Streamlit web interface provides:

- **📄 PRD Input**: Text input or file upload for requirements documents
- **🚀 One-Click Generation**: Generate complete Spring Boot projects instantly
- **🔧 MCP Validation Tools**:
  - Database schema validation with relationship detection
  - Entity design validation against Spring Boot best practices
  - Intelligent dependency suggestions based on requirements
- **📦 Code Download**: Download generated projects as ZIP files
- **📁 File Preview**: View generated project structure and files

### MCP Tools Available in UI

1. **Spring Boot Context** - Provides contextual information based on requirements
2. **Entity Validation** - Validates entity structures against Spring Boot best practices
3. **Database Schema Validation** - Validates relational database design and normalization
4. **Dependency Resolver** - Recommends Maven dependencies based on detected features
5. **API Best Practices** - REST API design guidelines
6. **Project Structure** - Recommended Spring Boot project layout

## � Sample PRD

Try the system with the included `sample_prd.md` file, which contains a complete Employee Management System specification.

## �🚀 What It Does

Upload a PRD (Product Requirements Document) and get:
- ✅ Complete Spring Boot starter project structure
- ✅ Entity models extracted from requirements
- ✅ CRUD REST endpoints for each entity
- ✅ Service and repository layers
- ✅ **Dynamic feature detection** and generation:
  - JWT or OAuth authentication
  - Database configuration (MySQL, PostgreSQL, MongoDB)
  - Caching (Redis)
  - Error handling
  - API documentation (Swagger)
  - Logging configuration
  - Role-based access control
  - Monitoring & health checks

## 🤖 MCP (Model Context Protocol) Integration

The system includes MCP server integration that provides Spring Boot best practices and validation:

### Available MCP Tools

1. **Spring Boot Context** (`get_spring_boot_context`)
   - Provides contextual information based on requirements
   - Includes best practices for entities, repositories, services, and controllers
   - Adapts context based on detected patterns (users, products, etc.)

2. **Entity Validation** (`validate_entity_design`)
   - Validates entity structures against Spring Boot best practices
   - Provides suggestions for improvements
   - Checks for required fields and proper naming

3. **Database Schema Validation** (`validate_database_schema`)
   - Validates relational database design and normalization
   - Suggests indexes for performance optimization
   - Identifies foreign key relationships
   - Checks for proper primary key setup

4. **Dependency Resolver** (`suggest_dependencies`)
   - Recommends Maven dependencies based on detected features
   - Categorizes dependencies (core, database, security, caching, etc.)
   - Generates complete pom.xml dependency sections
   - Adapts to requirements (MySQL, PostgreSQL, MongoDB, Redis, etc.)

5. **API Best Practices** (`get_api_best_practices`)
   - REST API design guidelines
   - HTTP status codes and response formats
   - Error handling recommendations

6. **Project Structure** (`generate_code_structure`)
   - Recommended Spring Boot project layout
   - Dependency suggestions
   - File organization best practices

### MCP API Endpoints

- `POST /mcp/context` - Get Spring Boot context for requirements
- `POST /mcp/validate-entity` - Validate entity design
- `POST /mcp/validate-database` - Validate database schema design
- `POST /mcp/suggest-dependencies` - Suggest Maven dependencies
- `GET /mcp/api-practices` - Get API best practices
- `POST /mcp/project-structure` - Generate project structure

## 📋 Overview

This project is an AI-powered smart developer assistant tool that converts business requirements (PRD documents) into a runnable Spring Boot project with intelligent feature detection and generation.
