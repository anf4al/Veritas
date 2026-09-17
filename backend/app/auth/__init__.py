"""Authentication and Authorization package."""
from backend.app.auth.permissions import (
    Permission,
    ROLE_PERMISSIONS,
    get_role_permissions,
    has_permission,
    check_document_access
)

__all__ = [
    "Permission",
    "ROLE_PERMISSIONS",
    "get_role_permissions",
    "has_permission",
    "check_document_access"
]
