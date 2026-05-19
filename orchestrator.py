"""MCP Client Orchestrator for Code Generation Pipeline.
Orchestrates the parser → analyzer → generator workflow via MCP server tools.
"""

import asyncio
from typing import Dict, Any

from tools.mcp_server import MCPServer


class MCPOrchestrator:
    """MCP Client that orchestrates the code generation pipeline by calling tools exposed by the MCP server."""

    def __init__(self):
        self.mcp_server = MCPServer()

    async def run_pipeline_async(self, file_path: str, project_name: str = "generated-project"):
        """Execute the full code generation pipeline via MCP tools asynchronously."""
        print(f"[Orchestrator] Starting pipeline for {file_path}")

        print(f"[Orchestrator] Step 1: Parsing PRD file...")
        parse_result = await self.mcp_server.call_tool_async("parse_prd", file_path=file_path)

        if not parse_result.get("success"):
            raise Exception(f"Parse failed: {parse_result.get('error')}")

        prd_text = parse_result["content"]
        print(f"[Orchestrator] Parsed {parse_result['length']} characters")

        print(f"[Orchestrator] Step 2: Analyzing PRD content...")
        analysis_result = await self.mcp_server.call_tool_async(
            "analyze_prd",
            prd_text=prd_text,
            project_name=project_name,
        )

        if not analysis_result.get("success"):
            raise Exception(f"Analysis failed: {analysis_result.get('error')}")

        analysis_data = analysis_result["analysis"]
        print(f"[Orchestrator] Analysis complete with {len(analysis_data.get('entities', []))} entities")

        print(f"[Orchestrator] Step 3: Generating Spring Boot project...")
        generation_result = await self.mcp_server.call_tool_async(
            "generate_project",
            analysis_data=analysis_data,
        )

        if not generation_result.get("success"):
            raise Exception(f"Generation failed: {generation_result.get('error')}")

        zip_path = generation_result["zip_path"]
        print(f"[Orchestrator] Pipeline complete: {zip_path}")
        return zip_path

    def run_pipeline(self, file_path: str, project_name: str = "generated-project"):
        """Synchronous wrapper for run_pipeline_async."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.run_pipeline_async(file_path, project_name))
        raise RuntimeError(
            "run_pipeline() cannot be used from a running event loop. Use run_pipeline_async() instead."
        )

    async def get_tool_info_async(self) -> Dict[str, Any]:
        """Get information about available MCP tools asynchronously."""
        return await self.mcp_server.get_tool_info_async()

    def get_tool_info(self) -> Dict[str, Any]:
        """Synchronous wrapper for get_tool_info_async."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.get_tool_info_async())
        raise RuntimeError(
            "get_tool_info() cannot be used from a running event loop. Use get_tool_info_async() instead."
        )


_orchestrator_instance = None


def get_orchestrator():
    """Get or create the MCP orchestrator singleton."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MCPOrchestrator()
    return _orchestrator_instance


def run_pipeline(file_path: str, project_name: str = "generated-project"):
    """Convenience function for backward compatibility."""
    orchestrator = get_orchestrator()
    return orchestrator.run_pipeline(file_path, project_name)
