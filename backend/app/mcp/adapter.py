from typing import Dict, Any, List
from backend.app.tools.registry import get_tool_registry

class MCPToolAdapter:
    """Adapts Veritas enterprise tools to Model Context Protocol (MCP) JSON-RPC specification."""

    def __init__(self):
        self.registry = get_tool_registry()

    def get_mcp_tools_list(self) -> List[Dict[str, Any]]:
        """Return tool definitions conforming to MCP tools/list response format."""
        mcp_tools = []
        for tool in self.registry.list_tools():
            mcp_tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.parameters_schema
            })
        return mcp_tools

    def handle_mcp_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        user: Any,
        tenant_id: str,
        db: Any
    ) -> Dict[str, Any]:
        """Execute tool and format response conforming to MCP tools/call response format."""
        result = self.registry.execute_tool(
            name=tool_name,
            arguments=arguments,
            user=user,
            tenant_id=tenant_id,
            db=db
        )

        is_error = "error" in result
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ],
            "isError": is_error,
            "raw_result": result
        }
