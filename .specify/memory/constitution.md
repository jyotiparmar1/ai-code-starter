<!--
Sync Impact Report (v1.0.0 - 2026-05-11)
- Version change: N/A → 1.0.0
- Modified principles: All 5 principles defined (AI-Driven Development, Template-Based Code Generation, Modular Pipeline Architecture, Quality Spring Boot Generation, Extensible Integration Framework)
- Added sections: Technology Stack, Development Workflow
- Removed sections: None
- Templates requiring updates: None (generic templates remain compatible)
- Follow-up TODOs: None
-->
# AI Code Accelerator Constitution

## Core Principles

### I. AI-Driven Development
All code generation and analysis must leverage AI capabilities through OpenRouter (with future Claude integration). AI prompts and responses must be structured, versioned, and testable. Manual code writing is prohibited for generated artifacts - all Spring Boot code must be AI-generated from templates.

### II. Template-Based Code Generation
Code generation exclusively uses Jinja2 templates stored in the templates/ folder. Templates must be modular, maintainable, and produce runnable Spring Boot applications. Template changes require testing against sample PRDs to ensure output quality.

### III. Modular Pipeline Architecture (NON-NEGOTIABLE)
Project follows strict parser → analyzer → generator pipeline. Each tool (parser.py, analyzer.py, generator.py) must be independently testable and maintain clear interfaces. Pipeline failures must be logged and recoverable without data loss.

### IV. Quality Spring Boot Generation
Generated projects must be immediately runnable Spring Boot applications. All generated code must compile, include proper dependencies (via pom.xml), and follow Spring Boot best practices. Generated ZIP files must be downloadable and deployable.

### V. Extensible Integration Framework
Architecture must support future integrations (MCP, JIRA, Test cases) through pluggable interfaces. Current MVP focuses on PRD processing, but all code must be designed for extension without breaking changes.

## Technology Stack

**Backend**: Python 3.x + FastAPI for REST API endpoints
**AI Integration**: OpenRouter API (free tier) with planned Claude upgrade
**Code Generation**: Jinja2 templating engine for Spring Boot artifacts
**Output**: Python zipfile module for downloadable project archives
**Document Processing**: Parser tools for extracting text from PRD/Jira/Test case documents
**Project Structure**: Modular tools/ folder with independent parser, analyzer, generator components

## Development Workflow

**MVP Focus**: PRD file upload → text extraction → AI analysis → Spring Boot generation → ZIP download
**Phased Development**: Current phase delivers PRD-only processing; future phases add MCP, JIRA, and Test case integrations
**Testing**: All pipeline components must have unit tests; integration tests required for end-to-end PRD processing
**Code Review**: All template changes and AI prompt modifications require review and testing
**Deployment**: FastAPI server must run locally and support file uploads up to reasonable limits

## Governance

Constitution supersedes all development practices. All features must align with AI-driven, template-based generation principles. Pipeline architecture changes require constitution amendments. MVP scope limited to PRD processing - future integrations must extend without breaking existing functionality. Use main.py as the primary entry point and orchestrator.py for pipeline coordination.

**Version**: 1.0.0 | **Ratified**: 2026-05-11 | **Last Amended**: 2026-05-11
