from typing import Dict, Any
from backend.app.mcp.adapter import MCPToolAdapter

class MCPServer:
    """Lightweight in-process MCP Server handling standard JSON-RPC requests."""

    def __init__(self):
        self.adapter = MCPToolAdapter()

    def process_rpc(self, rpc_request: Dict[str, Any], user: Any, tenant_id: str, db: Any) -> Dict[str, Any]:
        req_id = rpc_request.get("id", 1)
        method = rpc_request.get("method", "")
        params = rpc_request.get("params", {})

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": self.adapter.get_mcp_tools_list()
                }
            }
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})
            call_res = self.adapter.handle_mcp_call(
                tool_name=name,
                arguments=args,
                user=user,
                tenant_id=tenant_id,
                db=db
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": call_res
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found."
                }
            }

_mcp_server = None

def get_mcp_server() -> MCPServer:
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
