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