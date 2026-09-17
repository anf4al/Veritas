"""Document Ingestion Package for Veritas."""
from backend.app.ingestion.extractor import extract_text_from_file
from backend.app.ingestion.cleaner import clean_extracted_text
from backend.app.ingestion.chunker import chunk_document_text, ExtractedChunk
from backend.app.ingestion.pipeline import IngestionPipeline

__all__ = [
    "extract_text_from_file",
    "clean_extracted_text",
    "chunk_document_text",
    "ExtractedChunk",
    "IngestionPipeline"
]
