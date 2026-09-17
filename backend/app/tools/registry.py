from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.tools.base import EnterpriseTool
from backend.app.tools.knowledge import SearchEnterpriseKnowledgeTool
from backend.app.tools.documents import GetDocumentTool, CompareDocumentsTool, GetPolicyVersionsTool
from backend.app.tools.contracts import FindContractsExpiringTool
from backend.app.tools.vendor import GetVendorPerformanceTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, EnterpriseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        tools = [
            SearchEnterpriseKnowledgeTool(),
            GetDocumentTool(),
            CompareDocumentsTool(),
            FindContractsExpiringTool(),
            GetVendorPerformanceTool(),
            GetPolicyVersionsTool()
        ]
        for t in tools:
            self._tools[t.name] = t

    def get_tool(self, name: str) -> Optional[EnterpriseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[EnterpriseTool]:
        return list(self._tools.values())

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Export standardized tool schemas for OpenAI function-calling / MCP."""
        definitions = []
        for t in self._tools.values():
            definitions.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters_schema
                }
            })
        return definitions

    def execute_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        user: User,
        tenant_id: str,
        db: Session
    ) -> Dict[str, Any]:
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' not found."}
        try:
            return tool.execute(user=user, tenant_id=tenant_id, db=db, **arguments)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}

_registry_instance = None

def get_tool_registry() -> ToolRegistry:
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ToolRegistry()
    return _registry_instance

