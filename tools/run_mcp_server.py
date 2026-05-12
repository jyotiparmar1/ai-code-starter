#!/usr/bin/env python3
"""
MCP Server Runner for Spring Boot Assistant
Run this to start the MCP server independently
"""

import asyncio
from tools.mcp_server import server

async def main():
    """Run the MCP server"""
    print("Starting Spring Boot MCP Server...")
    print("Available tools:")
    for tool_name in server.list_tools():
        print(f"  - {tool_name}")

    # In a real implementation, you would set up proper MCP transport here
    # For now, this serves as a placeholder for server initialization
    print("MCP Server initialized. Tools are available for import.")

if __name__ == "__main__":
    asyncio.run(main())