import re

def clean_extracted_text(text: str) -> str:
    """Clean extracted document text:
    - normalize CRLF to LF
    - remove control characters except tabs/newlines
    - replace multiple consecutive blank lines with double newline
    - collapse excessive inline whitespace
    """
    if not text:
        return ""

    # Replace carriage returns
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove non-printable control characters
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    # Collapse multiple blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Collapse redundant horizontal spaces
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)

    return cleaned.strip()
