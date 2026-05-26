"""MCP Client Orchestrator for Code Generation Pipeline.
Orchestrates the parser → analyzer → generator workflow via MCP server tools.
"""

import asyncio
from typing import Dict, Any, List, Optional

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

    async def run_pipeline_with_jira_async(
        self,
        jira_issue_keys: List[str],
        project_name: str = "generated-project",
        prd_file_path: Optional[str] = None,
        jira_url: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_token: Optional[str] = None,
    ) -> str:
        """Pipeline using one or more JIRA issues as input, optionally merged with a PRD file."""
        print(f"[Orchestrator] Starting JIRA pipeline for {jira_issue_keys}")

        creds = dict(jira_url=jira_url, jira_email=jira_email, jira_token=jira_token)

        # Step 1: Fetch all JIRA issues and build per-issue metadata
        print(f"[Orchestrator] Step 1: Fetching {len(jira_issue_keys)} JIRA issue(s)...")
        issue_meta: List[Dict[str, Any]] = []  # {key, summary, content}
        project_key = ""
        combined_text = ""

        for key in jira_issue_keys:
            result = await self.mcp_server.call_tool_async(
                "fetch_jira_issue", issue_key=key, **creds
            )
            if not result.get("success"):
                raise Exception(f"JIRA fetch failed for {key}: {result.get('error')}")
            print(f"[Orchestrator]   Fetched {key}: {result.get('summary', '')}")
            issue_meta.append({
                "key": key,
                "summary": result.get("summary", ""),
                "content": result.get("content", ""),
            })
            if not project_key:
                project_key = result.get("project_key", "")

        # Combine content from all tickets (labelled by key)
        for meta in issue_meta:
            combined_text += f"\n\n## Ticket {meta['key']}: {meta['summary']}\n{meta['content']}"

        # Step 2: Sprint context from the first ticket's project
        print("[Orchestrator] Step 2: Fetching JIRA project context...")
        ctx_result = await self.mcp_server.call_tool_async(
            "fetch_jira_project_context", project_key=project_key, **creds
        )
        if ctx_result.get("success"):
            sprint_issues = ctx_result.get("sprint_issues", [])
            if sprint_issues:
                lines = [
                    f"- [{i['key']}] {i['summary']} ({i['type']}, {i['status']})"
                    for i in sprint_issues
                ]
                combined_text += "\n\n## Sprint Context\n" + "\n".join(lines)

        # Step 3: Optionally merge PRD file
        if prd_file_path:
            print("[Orchestrator] Step 3: Merging PRD file...")
            parse_result = await self.mcp_server.call_tool_async(
                "parse_prd", file_path=prd_file_path
            )
            if parse_result.get("success") and parse_result.get("content"):
                combined_text += "\n\n## Additional Requirements (PRD)\n" + parse_result["content"]

        # Step 4: Analyze
        print("[Orchestrator] Step 4: Analyzing combined requirements...")
        analysis_result = await self.mcp_server.call_tool_async(
            "analyze_prd", prd_text=combined_text, project_name=project_name
        )
        if not analysis_result.get("success"):
            raise Exception(f"Analysis failed: {analysis_result.get('error')}")
        analysis_data = analysis_result["analysis"]
        entities_data = analysis_data.get("entities", [])
        print(f"[Orchestrator] Found {len(entities_data)} entities")

        # Step 5: Generate
        print("[Orchestrator] Step 5: Generating Spring Boot project...")
        generation_result = await self.mcp_server.call_tool_async(
            "generate_project", analysis_data=analysis_data
        )
        if not generation_result.get("success"):
            raise Exception(f"Generation failed: {generation_result.get('error')}")
        zip_path = generation_result["zip_path"]

        # Step 6: Generate LLM summary + post contextual comment to each ticket
        print(f"[Orchestrator] Step 6: Posting comments to {len(jira_issue_keys)} ticket(s)...")
        for meta in issue_meta:
            # Ask LLM to write a comment tailored to this specific ticket
            print(f"[Orchestrator]   Generating LLM summary for {meta['key']}...")
            summary_result = await self.mcp_server.call_tool_async(
                "generate_jira_comment_summary",
                issue_summary=meta["summary"],
                issue_content=meta["content"],
                entities=entities_data,
            )
            llm_summary = summary_result.get("summary", "")
            if not summary_result.get("success"):
                print(f"[Orchestrator]   LLM summary fallback for {meta['key']}: {summary_result.get('error')}")

            comment_result = await self.mcp_server.call_tool_async(
                "post_jira_comment",
                issue_key=meta["key"],
                project_name=project_name,
                entities=entities_data,
                issue_summary=meta["summary"],
                all_issue_keys=jira_issue_keys,
                llm_summary=llm_summary,
                **creds,
            )
            if comment_result.get("success"):
                print(f"[Orchestrator]   Comment posted to {meta['key']}: {comment_result.get('comment_id')}")
            else:
                print(f"[Orchestrator]   Warning: comment not posted to {meta['key']}: {comment_result.get('error')}")

        print(f"[Orchestrator] JIRA pipeline complete: {zip_path}")
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
