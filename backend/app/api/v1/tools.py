from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.auth.dependencies import get_current_user, verify_tenant_access
from backend.app.models.user import User
from backend.app.tools.registry import get_tool_registry
from backend.app.mcp.server import get_mcp_server

router = APIRouter(prefix="/tools", tags=["Enterprise Tools & MCP"])

@router.get("")
def list_tools(current_user: User = Depends(get_current_user)):
    """List all registered enterprise tools and their schemas."""
    registry = get_tool_registry()
    tools = []
    for t in registry.list_tools():
        tools.append({
            "name": t.name,
            "description": t.description,
            "parameters": t.parameters_schema
        })
    return {"tools": tools}

@router.post("/execute")
def execute_tool(
    name: str = Body(..., embed=True),
    arguments: Dict[str, Any] = Body(default={}, embed=True),
    company_id: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a specific enterprise tool directly with authorization checks."""
    verify_tenant_access(current_user, company_id, db)
    registry = get_tool_registry()
    result = registry.execute_tool(
        name=name,
        arguments=arguments,
        user=current_user,
        tenant_id=company_id,
        db=db
    )
    return result

@router.post("/mcp/rpc")
def mcp_rpc(
    rpc_payload: Dict[str, Any] = Body(...),
    company_id: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Model Context Protocol (MCP) JSON-RPC 2.0 endpoint."""
    verify_tenant_access(current_user, company_id, db)
    server = get_mcp_server()
    return server.process_rpc(
        rpc_request=rpc_payload,
        user=current_user,
        tenant_id=company_id,
        db=db
    )
