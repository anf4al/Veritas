import os
import json
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.core.security import get_password_hash
from backend.app.models.company import Company
from backend.app.models.user import User, UserCompany
from backend.app.models.document import Document, Chunk
from backend.app.models.audit import AuditEvent
from backend.app.ingestion.pipeline import IngestionPipeline
from backend.scripts.generate_demo_dataset import COMPANIES, SEED_DIR, generate_all_seed_data

DEMO_USERS = [
    {
        "username": "admin@veritas.demo",
        "password": "VeritasAdmin!2026",
        "display_name": "Veritas Administrator",
        "role": "PLATFORM_ADMIN",
        "company_slugs": ["asterion", "northstar", "meridian"]
    },
    {
        "username": "hr@asterion.demo",
        "password": "VeritasHR!2026",
        "display_name": "Asterion HR Lead",
        "role": "HR_MANAGER",
        "company_slugs": ["asterion"]
    },
    {
        "username": "ops@asterion.demo",
        "password": "VeritasOps!2026",
        "display_name": "Asterion Operations Director",
        "role": "OPERATIONS_MANAGER",
        "company_slugs": ["asterion"]
    },
    {
        "username": "security@asterion.demo",
        "password": "VeritasSec!2026",
        "display_name": "Asterion Chief InfoSec Officer",
        "role": "SECURITY_OFFICER",
        "company_slugs": ["asterion"]
    },
    {
        "username": "sales@asterion.demo",
        "password": "VeritasSales!2026",
        "display_name": "Asterion Enterprise Sales Lead",
        "role": "SALES",
        "company_slugs": ["asterion"]
    },
    {
        "username": "employee@asterion.demo",
        "password": "VeritasEmployee!2026",
        "display_name": "Asterion Software Engineer",
        "role": "EMPLOYEE",
        "company_slugs": ["asterion"]
    },
    {
        "username": "admin@northstar.demo",
        "password": "NorthstarAdmin!2026",
        "display_name": "Northstar Plant Administrator",
        "role": "COMPANY_ADMIN",
        "company_slugs": ["northstar"]
    },
    {
        "username": "compliance@meridian.demo",
        "password": "MeridianCompliance!2026",
        "display_name": "Meridian HIPAA Compliance Officer",
        "role": "COMPLIANCE_OFFICER",
        "company_slugs": ["meridian"]
    }
]

def seed_database(reset: bool = True):
    from backend.app.models.evaluation import EvaluationRun, EvaluationResult
    from backend.app.retrieval.vector_store import get_vector_store

    if reset:
        print("Dropping existing tables for clean seed...")
        Base.metadata.drop_all(bind=engine)
        # Clear vector store memory
        store = get_vector_store()
        store._tenants.clear()
        store._matrices.clear()

    print("Recreating database schema...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # 1. Seed Companies
    company_map = {}
    for comp in COMPANIES:
        existing = db.query(Company).filter(Company.slug == comp["slug"]).first()
        if not existing:
            c = Company(
                name=comp["name"],
                slug=comp["slug"],
                description=comp["description"]
            )
            db.add(c)
            db.flush()
            company_map[comp["slug"]] = c
            print(f"Created company: {c.name}")
        else:
            company_map[comp["slug"]] = existing

    db.commit()

    # 2. Seed Users & Memberships
    admin_user = None
    for u_info in DEMO_USERS:
        existing_u = db.query(User).filter(User.username == u_info["username"]).first()
        if not existing_u:
            new_u = User(
                username=u_info["username"],
                password_hash=get_password_hash(u_info["password"]),
                display_name=u_info["display_name"],
                role=u_info["role"]
            )
            db.add(new_u)
            db.flush()
            print(f"Created demo user: {new_u.username} [{new_u.role}]")

            for slug in u_info["company_slugs"]:
                c = company_map.get(slug)
                if c:
                    membership = UserCompany(user_id=new_u.id, company_id=c.id)
                    db.add(membership)
            if new_u.role == "PLATFORM_ADMIN":
                admin_user = new_u
        else:
            if existing_u.role == "PLATFORM_ADMIN":
                admin_user = existing_u

    db.commit()

    # 3. Ensure seed documents exist on disk and regenerate to include handbook
    print("Regenerating demo dataset to ensure all current enterprise policies exist...")
    generate_all_seed_data()

    meta_file = SEED_DIR / "metadata.json"
    with open(meta_file, "r", encoding="utf-8") as f:
        doc_metadata = json.load(f)

    # 4. Ingest documents into database & vector store
    pipeline = IngestionPipeline(db=db)
    admin_id = admin_user.id if admin_user else None

    total_docs = len(doc_metadata)
    print(f"Ingesting and indexing {total_docs} enterprise documents...")

    ingested_count = 0
    for idx, item in enumerate(doc_metadata, start=1):
        slug = item["company_slug"]
        company = company_map.get(slug)
        if not company:
            continue

        file_path = SEED_DIR / item["relative_path"]
        if not file_path.exists():
            continue

        # Check if already ingested
        existing_doc = db.query(Document).filter(
            Document.company_id == company.id,
            Document.filename == item["filename"]
        ).first()

        if not existing_doc:
            pipeline.ingest_file(
                file_path=file_path,
                company_id=company.id,
                title=item["title"],
                department=item["department"],
                document_type=item["document_type"],
                version=item["version"],
                effective_date=item["effective_date"],
                confidentiality=item["confidentiality"],
                user_id=admin_id
            )
            ingested_count += 1
            if idx % 30 == 0 or idx == total_docs:
                print(f"Progress: {idx}/{total_docs} documents processed.")

    db.commit()
    db.close()
    print(f"Database seeding completed! Ingested {ingested_count} new documents.")

    # Automatically generate and link authentic enterprise PDFs
    from backend.scripts.generate_seed_pdfs import generate_all_seed_pdfs
    generate_all_seed_pdfs()

if __name__ == "__main__":
    seed_database()

