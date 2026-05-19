"""
MCP Client Orchestrator for Code Generation Pipeline
Orchestrates the parser → analyzer → generator workflow via MCP server tools.
"""

from tools.mcp_server import MCPServer


class MCPOrchestrator:
    """
    MCP Client that orchestrates the code generation pipeline
    by calling tools exposed by the MCP server.
    """

    def __init__(self):
        """Initialize the MCP orchestrator with the MCP server"""
        self.mcp_server = MCPServer()

    def run_pipeline(self, file_path: str, project_name: str = "generated-project"):
        """
        Execute the full code generation pipeline via MCP tools.
        
        Args:
            file_path: Path to the PRD file
            project_name: Name for the generated project
            
        Returns:
            Path to the generated project ZIP file
        """
        print(f"[Orchestrator] Starting pipeline for {file_path}")
        
        # Step 1: Parse the PRD file
        print(f"[Orchestrator] Step 1: Parsing PRD file...")
        parse_result = self.mcp_server.call_tool("parse_prd", file_path=file_path)
        
        if not parse_result.get("success"):
            raise Exception(f"Parse failed: {parse_result.get('error')}")
        
        prd_text = parse_result["content"]
        print(f"[Orchestrator] Parsed {parse_result['length']} characters")
        
        # Step 2: Analyze the PRD text
        print(f"[Orchestrator] Step 2: Analyzing PRD content...")
        analysis_result = self.mcp_server.call_tool("analyze_prd", prd_text=prd_text, project_name=project_name)
        
        if not analysis_result.get("success"):
            raise Exception(f"Analysis failed: {analysis_result.get('error')}")
        
        analysis_data = analysis_result["analysis"]
        print(f"[Orchestrator] Analysis complete with {len(analysis_data.get('entities', []))} entities")
        
        # Step 2.5: Validate and enhance analysis data
        print(f"[Orchestrator] Step 2.5: Validating and enhancing analysis...")
        validation_results = self._validate_and_enhance_analysis(analysis_data, prd_text)
        analysis_data.update(validation_results)
        print(f"[Orchestrator] Validation complete - {len(validation_results.get('validation_issues', []))} issues found")
        
        # Step 3: Generate the Spring Boot project
        print(f"[Orchestrator] Step 3: Generating Spring Boot project...")
        generation_result = self.mcp_server.call_tool("generate_project", analysis_data=analysis_data)
        
        if not generation_result.get("success"):
            raise Exception(f"Generation failed: {generation_result.get('error')}")
        
        zip_path = generation_result["zip_path"]
        print(f"[Orchestrator] Pipeline complete: {zip_path}")
        
        return zip_path

    def get_tool_info(self):
        """
        Get information about available MCP tools.
        
        Returns:
            Dictionary with tool names and descriptions
        """
        tools_info = {}
        for tool_name, tool_config in self.mcp_server.tools.items():
            tools_info[tool_name] = {
                "description": tool_config.get("description"),
                "inputSchema": tool_config.get("inputSchema")
            }
        return tools_info


    def _validate_and_enhance_analysis(self, analysis_data: dict, prd_text: str) -> dict:
        """
        Validate analysis data and enhance with suggestions.
        
        Args:
            analysis_data: The analysis result from the analyzer
            prd_text: Original PRD text for dependency suggestions
            
        Returns:
            Dictionary with validation results and enhancements
        """
        enhancements = {
            "validation_issues": [],
            "validation_suggestions": [],
            "recommended_dependencies": {},
            "database_indexes": [],
            "entity_relationships": []
        }
        
        entities = analysis_data.get("entities", [])
        
        # Validate entity designs
        for entity in entities:
            entity_validation = self.mcp_server.validate_entity_design(entity)
            if not entity_validation.get("valid"):
                enhancements["validation_issues"].extend(entity_validation.get("issues", []))
            enhancements["validation_suggestions"].extend(entity_validation.get("suggestions", []))
        
        # Validate database schema
        if entities:
            schema_validation = self.mcp_server.validate_database_schema({"entities": entities})
            enhancements["validation_issues"].extend(schema_validation.get("issues", []))
            enhancements["validation_suggestions"].extend(schema_validation.get("suggestions", []))
            enhancements["database_indexes"] = schema_validation.get("indexes", [])
            enhancements["entity_relationships"] = schema_validation.get("relationships", [])
        
        # Suggest dependencies based on analysis and PRD text
        features_data = {
            "requirements": prd_text,
            "entities": entities
        }
        dependency_suggestions = self.mcp_server.suggest_dependencies(features_data)
        enhancements["recommended_dependencies"] = dependency_suggestions.get("dependencies", {})
        
        return enhancements


# Create a singleton orchestrator instance
_orchestrator_instance = None


def get_orchestrator():
    """Get or create the MCP orchestrator singleton"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MCPOrchestrator()
    return _orchestrator_instance


def run_pipeline(file_path: str, project_name: str = "generated-project"):
    """
    Convenience function for backward compatibility.
    Runs the MCP pipeline through the orchestrator.
    
    Args:
        file_path: Path to the PRD file
        project_name: Name for the generated project
        
    Returns:
        Path to the generated project ZIP file
    """
    orchestrator = get_orchestrator()
    return orchestrator.run_pipeline(file_path, project_name)