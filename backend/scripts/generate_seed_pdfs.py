import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

from backend.app.core.database import SessionLocal
from backend.app.core.config import settings
from backend.app.models.company import Company
from backend.app.models.document import Document

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print 'Page X of Y' in footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(0.75 * inch, 0.65 * inch, letter[0] - 0.75 * inch, 0.65 * inch)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 0.75 * inch, 0.45 * inch, page_str)
        self.drawString(0.75 * inch, 0.45 * inch, "Veritas Enterprise Intelligence Platform | Authoritative Record")

        # Header (on pages after the first)
        if self._pageNumber > 1:
            self.line(0.75 * inch, letter[1] - 0.55 * inch, letter[0] - 0.75 * inch, letter[1] - 0.55 * inch)
            self.drawString(0.75 * inch, letter[1] - 0.45 * inch, getattr(self, "doc_title", "Enterprise Document"))
            self.drawRightString(letter[0] - 0.75 * inch, letter[1] - 0.45 * inch, getattr(self, "doc_company", ""))

        self.restoreState()

def parse_markdown_to_flowables(
    text: str,
    doc_meta: Dict[str, Any],
    styles: Any
) -> List[Any]:
    """Parse Markdown text into styled ReportLab flowables."""
    flowables = []

    # 1. Document Title & Company Header
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )

    company_style = ParagraphStyle(
        "DocCompany",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=12
    )

    flowables.append(Paragraph(doc_meta.get("title", "Enterprise Document"), title_style))
    flowables.append(Paragraph(doc_meta.get("company_name", "Enterprise Organization").upper(), company_style))

    # 2. Metadata Box Table
    meta_data = [
        [
            Paragraph("<b>Document ID:</b>", styles["MetaKey"]),
            Paragraph(doc_meta.get("doc_id", "N/A"), styles["MetaVal"]),
            Paragraph("<b>Department:</b>", styles["MetaKey"]),
            Paragraph(doc_meta.get("department", "General"), styles["MetaVal"])
        ],
        [
            Paragraph("<b>Version:</b>", styles["MetaKey"]),
            Paragraph(f"v{doc_meta.get('version', '1.0')}", styles["MetaVal"]),
            Paragraph("<b>Effective Date:</b>", styles["MetaKey"]),
            Paragraph(doc_meta.get("effective_date", "N/A"), styles["MetaVal"])
        ],
        [
            Paragraph("<b>Classification:</b>", styles["MetaKey"]),
            Paragraph(doc_meta.get("confidentiality", "internal").upper(), styles["MetaVal"]),
            Paragraph("<b>Document Type:</b>", styles["MetaKey"]),
            Paragraph(doc_meta.get("document_type", "Policy").title(), styles["MetaVal"])
        ]
    ]

    meta_table = Table(meta_data, colWidths=[1.3 * inch, 1.95 * inch, 1.3 * inch, 1.95 * inch])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    flowables.append(meta_table)
    flowables.append(Spacer(1, 14))

    # 3. Process markdown body content
    paragraphs = text.split("\n\n")
    in_table = False
    table_lines: List[str] = []

    for para in paragraphs:
        stripped = para.strip()
        if not stripped:
            continue

        lines = stripped.split("\n")

        # Check if this block is a table
        if all(l.strip().startswith("|") and l.strip().endswith("|") for l in lines if l.strip()):
            table_rows = []
            for l in lines:
                l_str = l.strip()
                if "---" in l_str:
                    continue  # Divider row
                cells = [c.strip() for c in l_str.strip("|").split("|")]
                table_rows.append([Paragraph(c, styles["TableBody"]) for c in cells])

            if table_rows:
                # Format table
                col_width = (letter[0] - 1.5 * inch) / max(1, len(table_rows[0]))
                col_widths = [col_width] * len(table_rows[0])
                r_table = Table(table_rows, colWidths=col_widths)
                r_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]))
                flowables.append(Spacer(1, 6))
                flowables.append(r_table)
                flowables.append(Spacer(1, 8))
            continue

        # Check for headings
        if stripped.startswith("#"):
            h_match = re.match(r"^(#+)\s*(.*)", stripped)
            if h_match:
                level = len(h_match.group(1))
                h_text = h_match.group(2).strip()
                if level == 1:
                    flowables.append(Spacer(1, 10))
                    flowables.append(Paragraph(h_text, styles["Heading1Custom"]))
                    flowables.append(Spacer(1, 4))
                elif level == 2:
                    flowables.append(Spacer(1, 8))
                    flowables.append(Paragraph(h_text, styles["Heading2Custom"]))
                    flowables.append(Spacer(1, 3))
                else:
                    flowables.append(Spacer(1, 6))
                    flowables.append(Paragraph(h_text, styles["Heading3Custom"]))
                    flowables.append(Spacer(1, 2))
                continue

        # Check numbered / bullet clauses
        if re.match(r"^[0-9]+(?:\.[0-9]+)*\s+[A-Z]", stripped):
            flowables.append(Paragraph(stripped.replace("\n", "<br/>"), styles["ClauseCustom"]))
            flowables.append(Spacer(1, 4))
        else:
            # Regular paragraph
            safe_p = stripped.replace("&", "&amp;").replace("<br>", "<br/>")
            # Convert basic markdown bolding
            safe_p = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", safe_p)
            safe_p = safe_p.replace("\n", "<br/>")
            flowables.append(Paragraph(safe_p, styles["BodyCustom"]))
            flowables.append(Spacer(1, 5))

    return flowables

def generate_pdf_for_document(
    doc: Document,
    company: Company,
    markdown_path: Path,
    output_pdf_path: Path
) -> bool:
    """Render markdown seed file into genuine, beautifully formatted PDF."""
    if not markdown_path.exists():
        return False

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Styles
    base_styles = getSampleStyleSheet()

    styles = {
        "Normal": base_styles["Normal"],
        "MetaKey": ParagraphStyle("MetaKey", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.HexColor("#475569")),
        "MetaVal": ParagraphStyle("MetaVal", fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#0F172A")),
        "Heading1Custom": ParagraphStyle("H1C", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.HexColor("#0F172A")),
        "Heading2Custom": ParagraphStyle("H2C", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=colors.HexColor("#1E293B")),
        "Heading3Custom": ParagraphStyle("H3C", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.HexColor("#334155")),
        "ClauseCustom": ParagraphStyle("ClauseC", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#0F172A")),
        "BodyCustom": ParagraphStyle("BodyC", fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#334155")),
        "TableBody": ParagraphStyle("TableB", fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#0F172A")),
    }

    doc_meta = {
        "title": doc.title,
        "company_name": company.name,
        "doc_id": doc.filename.rsplit(".", 1)[0].upper(),
        "department": doc.department,
        "version": doc.version,
        "effective_date": doc.effective_date or "2026-01-01",
        "confidentiality": doc.confidentiality,
        "document_type": doc.document_type
    }

    flowables = parse_markdown_to_flowables(md_text, doc_meta, styles)

    doc_template = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    canvas_factory = lambda *args, **kwargs: NumberedCanvas(*args, **kwargs)

    # Set canvas attributes for header
    def on_page_start(canvas_obj, doc_obj):
        canvas_obj.doc_title = doc.title
        canvas_obj.doc_company = company.name

    doc_template.build(flowables, canvasmaker=canvas_factory, onFirstPage=on_page_start, onLaterPages=on_page_start)
    return True

def generate_all_seed_pdfs():
    """Convert all existing enterprise documents into genuine PDFs and update DB storage_path."""
    db: Session = SessionLocal()
    try:
        documents = db.query(Document).all()
        print(f"Generating genuine enterprise PDFs for {len(documents)} documents...")

        converted_count = 0
        for doc in documents:
            company = db.query(Company).filter(Company.id == doc.company_id).first()
            if not company:
                continue

            # Check where markdown file resides
            md_path = settings.SEED_DATA_DIR / company.slug / doc.filename
            if not md_path.exists():
                # Fallback: check with .md suffix if doc.filename doesn't have it
                md_path = settings.SEED_DATA_DIR / company.slug / f"{doc.filename}.md"

            if not md_path.exists():
                continue

            # Target PDF path
            pdf_filename = f"{doc.id}.pdf"
            pdf_path = settings.STORAGE_DIR / "documents" / company.id / pdf_filename

            success = generate_pdf_for_document(
                doc=doc,
                company=company,
                markdown_path=md_path,
                output_pdf_path=pdf_path
            )

            if success:
                doc.storage_path = str(pdf_path)
                converted_count += 1
                if converted_count % 30 == 0:
                    print(f"Progress: {converted_count}/{len(documents)} PDFs generated.")

        db.commit()
        print(f"Successfully generated {converted_count} genuine enterprise PDFs and linked storage_path!")
    finally:
        db.close()

if __name__ == "__main__":
    generate_all_seed_pdfs()

