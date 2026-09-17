from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.user import User
from backend.app.models.document import Document, Chunk
from backend.app.tools.base import EnterpriseTool
from backend.app.auth.permissions import check_document_access

class GetVendorPerformanceTool(EnterpriseTool):
    name = "get_vendor_performance"
    description = (
        "Retrieve vendor performance reports, SLA breach records, and risk assessments "
        "for a specific vendor (e.g. 'Vendor Atlas')."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "vendor_name": {
                "type": "string",
                "description": "The name of the vendor (e.g. 'Vendor Atlas', 'Apex Logistics')."
            }
        },
        "required": ["vendor_name"]
    }

    def execute(self, user: User, tenant_id: str, db: Session, **kwargs) -> Dict[str, Any]:
        vendor_name = kwargs.get("vendor_name", "").strip()
        if not vendor_name:
            return {"error": "vendor_name is required."}

        # Search for documents mentioning vendor_name in title or chunks
        docs = db.query(Document).filter(
            Document.company_id == tenant_id,
            Document.title.ilike(f"%{vendor_name}%")
        ).all()

        results = []
        for d in docs:
            if not check_document_access(user.role, d.department, d.confidentiality, d.document_type, d.title):
                continue

            chunks = db.query(Chunk).filter(Chunk.document_id == d.id).order_by(Chunk.chunk_index).all()
            excerpt = "\n".join([c.text for c in chunks[:2]])
            results.append({
                "document_id": d.id,
                "title": d.title,
                "document_type": d.document_type,
                "department": d.department,
                "effective_date": d.effective_date,
                "version": d.version,
                "summary_excerpt": excerpt[:800]
            })

        return {
            "vendor_name": vendor_name,
            "reports_found": len(results),
            "performance_records": results
        }

