from enum import Enum

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
)

from core.loaders.adobe_express_loader import AdobeExpressLoader


class FileType(Enum):
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "txt"
    ADOBE_EXPRESS = "adobe_express"


LOADERS = (
    (FileType.PDF, PyPDFLoader),
    (FileType.DOCX, UnstructuredWordDocumentLoader),
    (FileType.TEXT, TextLoader),
    (FileType.ADOBE_EXPRESS, AdobeExpressLoader),
)


def load_document(url: str, file_type: FileType) -> list:
    """Load a single document from the given file path or url."""

    for ft, loader_cls in LOADERS:
        if ft == file_type:
            if file_type == FileType.ADOBE_EXPRESS:
                loader = loader_cls(url)
            else:
                loader = loader_cls(url)
            return loader.load()
    raise ValueError(f"Unsupported file type: {file_type}")
