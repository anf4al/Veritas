import re
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ExtractedChunk:
    chunk_index: int
    text: str
    page: int
    section: Optional[str] = None
    metadata_json: Dict[str, Any] = field(default_factory=dict)

def detect_section_heading(line: str) -> Optional[str]:
    """Detect section heading lines such as '## 3. SLA Targets', 'Section 14.2 Termination', 'ARTICLE IV'."""
    stripped = line.strip()
    # Markdown heading
    if stripped.startswith("#"):
        return re.sub(r"^#+\s*", "", stripped).strip()
    # Section or Article prefix
    match = re.match(r"^(section|article|part|chapter|policy|appendix)\s+([0-9A-Z\.]+.*)", stripped, re.IGNORECASE)
    if match:
        return stripped
    # Numbered heading e.g. "1.2 Scope"
    if re.match(r"^[0-9]+(\.[0-9]+)+\s+[A-Z]", stripped):
        return stripped
    return None

def chunk_document_text(
    pages: List[Tuple[int, str]],
    target_chunk_size: int = 1200,
    overlap_size: int = 150
) -> List[ExtractedChunk]:
    """Chunk document preserving page numbers, section headers, and semantic boundaries."""
    chunks: List[ExtractedChunk] = []
    chunk_index = 0
    current_section = "General"

    for page_num, page_text in pages:
        if not page_text.strip():
            continue

        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
        current_chunk_text = ""

        for para in paragraphs:
            # Check if paragraph begins with a section heading
            first_line = para.split("\n")[0]
            heading = detect_section_heading(first_line)
            if heading:
                current_section = heading

            if len(current_chunk_text) + len(para) <= target_chunk_size:
                if current_chunk_text:
                    current_chunk_text += "\n\n" + para
                else:
                    current_chunk_text = para
            else:
                if current_chunk_text:
                    chunks.append(ExtractedChunk(
                        chunk_index=chunk_index,
                        text=current_chunk_text.strip(),
                        page=page_num,
                        section=current_section,
                        metadata_json={"page": page_num, "section": current_section}
                    ))
                    chunk_index += 1
                    # Modest overlap from previous chunk
                    overlap = current_chunk_text[-overlap_size:] if len(current_chunk_text) > overlap_size else ""
                    current_chunk_text = (overlap + "\n\n" + para).strip()
                else:
                    # Paragraph itself is larger than target_chunk_size: split by sentences/lines
                    lines = para.split("\n")
                    sub_buf = ""
                    for line in lines:
                        if len(sub_buf) + len(line) <= target_chunk_size:
                            sub_buf += ("\n" if sub_buf else "") + line
                        else:
                            if sub_buf:
                                chunks.append(ExtractedChunk(
                                    chunk_index=chunk_index,
                                    text=sub_buf.strip(),
                                    page=page_num,
                                    section=current_section,
                                    metadata_json={"page": page_num, "section": current_section}
                                ))
                                chunk_index += 1
                            sub_buf = line
                    current_chunk_text = sub_buf

        if current_chunk_text.strip():
            chunks.append(ExtractedChunk(
                chunk_index=chunk_index,
                text=current_chunk_text.strip(),
                page=page_num,
                section=current_section,
                metadata_json={"page": page_num, "section": current_section}
            ))
            chunk_index += 1

    return chunks

