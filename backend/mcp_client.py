import httpx
import json
from typing import Any, Dict, List, Optional


class MCPClient:
    """Client for interacting with MCP (Model Context Protocol) servers"""

    def __init__(self, server_url: str):
        """
        Initialize MCP client

        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = 30.0

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server

        Returns:
            List of tool definitions
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.server_url}/tools",
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json().get("tools", [])
                else:
                    print(f"Error listing tools: {response.status_code}")
                    return []
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """
        Call a tool on the MCP server

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool result or None if error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.server_url}/tools/{tool_name}",
                    json={"arguments": arguments},
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    return response.json().get("result")
                else:
                    print(f"Error calling tool {tool_name}: {response.status_code}")
                    return None
        except Exception as e:
            print(f"Error calling tool {tool_name}: {e}")
            return None

    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls

        Args:
            tool_calls: List of tool calls with format:
                [{"name": "tool_name", "arguments": {...}}, ...]

        Returns:
            List of results
        """
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})

            result = await self.call_tool(tool_name, arguments)
            results.append({
                "tool": tool_name,
                "result": result
            })

        return results


class MCPManager:
    """Manager for multiple MCP servers"""

    def __init__(self):
        self.servers: Dict[str, MCPClient] = {}

    def add_server(self, name: str, url: str):
        """Add an MCP server"""
        self.servers[name] = MCPClient(url)

    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List tools from all servers"""
        all_tools = {}
        for name, server in self.servers.items():
            tools = await server.list_tools()
            all_tools[name] = tools
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Call a tool on a specific server"""
        if server_name in self.servers:
            return await self.servers[server_name].call_tool(tool_name, arguments)
        return None


# Example usage and tool call parsing
def parse_gemini_tool_calls(response_text: str) -> List[Dict[str, Any]]:
    """
    Parse tool calls from Gemini response

    This is a simple parser - you may need to adjust based on
    how Gemini formats tool calls in its responses

    Args:
        response_text: Response text from Gemini

    Returns:
        List of parsed tool calls
    """
    tool_calls = []

    # Look for common patterns like:
    # "I'll use the [tool_name] tool with arguments: {...}"
    # Or structured JSON tool calls

    # For now, return empty list
    # This should be enhanced based on actual Gemini output format
    return tool_calls
