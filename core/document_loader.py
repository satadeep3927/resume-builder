from enum import Enum

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
)

from core.loaders.adobe_acrobat_loader import AdobeAcrobatLoader
from core.loaders.adobe_express_loader import AdobeExpressLoader


class FileType(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "txt"
    ADOBE_EXPRESS = "adobe_express"
    ADOBE_ACROBAT = "adobe_acrobat"


LOADERS = (
    (FileType.PDF, PyPDFLoader),
    (FileType.DOCX, UnstructuredWordDocumentLoader),
    (FileType.TEXT, TextLoader),
    (FileType.ADOBE_EXPRESS, AdobeExpressLoader),
    (FileType.ADOBE_ACROBAT, AdobeAcrobatLoader),
)


def load_document(url: str, file_type: FileType) -> list:
    """Load a single document from the given file path or url."""

    for ft, loader_cls in LOADERS:
        if ft == file_type:
            if file_type in [FileType.ADOBE_EXPRESS, FileType.ADOBE_ACROBAT]:
                loader = loader_cls(url)
            else:
                loader = loader_cls(url)
            return loader.load()
    raise ValueError(f"Unsupported file type: {file_type}")


def detect_file_type(url_or_path: str) -> FileType:
    """Detect file type from URL or file path."""
    url_lower = url_or_path.lower()

    # Check for Adobe URLs
    if "new.express.adobe.com" in url_lower:
        return FileType.ADOBE_EXPRESS
    elif "acrobat.adobe.com" in url_lower or "urn:aaid:sc:AP:" in url_lower:
        return FileType.ADOBE_ACROBAT

    # Check file extensions
    if url_lower.endswith(".pdf"):
        return FileType.PDF
    elif url_lower.endswith(".docx") or url_lower.endswith(".doc"):
        return FileType.DOCX
    elif url_lower.endswith(".txt"):
        return FileType.TEXT

    # Default fallback
    raise ValueError(f"Cannot detect file type from: {url_or_path}")
