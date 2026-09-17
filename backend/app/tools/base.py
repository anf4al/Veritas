from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User

class EnterpriseTool(ABC):
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    @abstractmethod
    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        """Execute tool logic enforcing user role, tenant isolation, and parameter validation."""
        pass
