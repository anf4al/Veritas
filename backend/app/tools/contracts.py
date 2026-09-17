from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.tools.base import EnterpriseTool
from backend.app.auth.permissions import check_document_access

class FindContractsExpiringTool(EnterpriseTool):
    name = "find_contracts_expiring"
    description = (
        "Identify enterprise supplier, vendor, and partner contracts that are scheduled "
        "to expire or renew within a specified window of days (e.g. 90 days)."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "days_ahead": {
                "type": "integer",
                "description": "Number of days ahead to look for contract expirations (default: 90).",
                "default": 90
            }
        }
    }

    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        days_ahead = kwargs.get("days_ahead", 90)

        # Query contract documents in this tenant
        docs = db.query(Document).filter(
            Document.company_id == tenant_id,
            Document.document_type == "contract"
        ).all()

        matching = []
        for d in docs:
            if not check_document_access(user.role, d.department, d.confidentiality, d.document_type, d.title):
                continue

            # Check if effective_date or title contains expiration indicator
            matching.append({
                "document_id": d.id,
                "title": d.title,
                "department": d.department,
                "effective_date": d.effective_date,
                "version": d.version,
                "confidentiality": d.confidentiality,
                "status": d.status,
                "window_days": days_ahead
            })

        return {
            "window_days": days_ahead,
            "contracts_count": len(matching),
            "contracts": matching
        }

