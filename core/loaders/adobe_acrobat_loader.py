import logging
import os
import tempfile

import bs4
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document

from schema.adobe import Acrobat

logger = logging.getLogger(__name__)


class AdobeAcrobatLoader(BaseLoader):
    """
    Adobe Acrobat PDF Loader

    Loads PDFs from Adobe Acrobat share URLs by:
    1. Fetching the share page HTML
    2. Extracting the PDF download URL from the embedded JSON data
    3. Downloading the PDF file
    4. Loading content using PyPDFLoader
    """

    def __init__(self, url: str, timeout: int = 30):
        """
        Initialize the Adobe Acrobat loader.

        Args:
            url: Adobe Acrobat share URL (e.g., https://acrobat.adobe.com/id/urn:aaid:sc:AP:...)
            timeout: Request timeout in seconds (default: 30)
        """
        if not isinstance(url, str) or not url.startswith("https://"):
            raise ValueError(
                "Invalid Adobe Acrobat URL. Must be a string starting with https://"
            )

        if "acrobat.adobe.com" not in url:
            raise ValueError(
                "Invalid Adobe Acrobat URL. Must be from acrobat.adobe.com domain"
            )

        self.url = url
        self.timeout = timeout
        logger.info(f"Initialized AdobeAcrobatLoader with URL: {url}")

    def _fetch_page_html(self) -> str:
        """
        Fetch the HTML content from the Adobe Acrobat share page.

        Returns:
            str: The HTML content of the page

        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response is empty or invalid
        """
        try:
            logger.info(f"Fetching HTML from: {self.url}")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            response = requests.get(self.url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            if not response.text.strip():
                raise ValueError("Received empty response from Adobe Acrobat")

            logger.info(
                f"Successfully fetched HTML content ({len(response.text)} characters)"
            )
            return response.text

        except requests.RequestException as e:
            logger.error(f"Failed to fetch HTML from {self.url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching HTML: {e}")
            raise ValueError(f"Failed to fetch Adobe Acrobat page: {e}")

    def _extract_pdf_url(self, html: str) -> str:
        """
        Extract the PDF download URL from the HTML page.

        Args:
            html: The HTML content of the Adobe Acrobat page

        Returns:
            str: The PDF download URL

        Raises:
            ValueError: If the required data cannot be found or parsed
        """
        try:
            logger.info("Parsing HTML to extract PDF download URL")

            document = bs4.BeautifulSoup(html, "html.parser")

            # Look for the data element
            element = document.find(id="dc_data")
            if not element:
                logger.error("Could not find #dc_data element in HTML")
                raise ValueError(
                    "Could not find the required data element (#dc_data) in the HTML"
                )

            json_text = element.get_text(strip=True)
            if not json_text:
                raise ValueError("Found #dc_data element but it contains no data")

            logger.info(f"Found JSON data ({len(json_text)} characters)")

            # Parse the JSON data using the Acrobat schema
            try:
                data = Acrobat.model_validate_json(json_text)
            except Exception as e:
                logger.error(f"Failed to parse JSON data: {e}")
                raise ValueError(f"Failed to parse Adobe Acrobat data: {e}")

            # Extract the download URL
            try:
                download_url = data.data.file.assetURLs.download_url
                if not download_url:
                    raise ValueError("Download URL is empty in the parsed data")

                logger.info(
                    f"Successfully extracted PDF download URL: {download_url[:100]}..."
                )
                return download_url

            except AttributeError as e:
                logger.error(f"Invalid data structure in Adobe response: {e}")
                raise ValueError(f"Invalid Adobe Acrobat data structure: {e}")

        except Exception as e:
            logger.error(f"Failed to extract PDF URL: {e}")
            raise

    def _download_pdf(self, pdf_url: str) -> bytes:
        """
        Download the PDF content from the extracted URL.

        Args:
            pdf_url: The PDF download URL

        Returns:
            bytes: The PDF file content

        Raises:
            requests.RequestException: If the download fails
            ValueError: If the downloaded content is invalid
        """
        try:
            logger.info(f"Downloading PDF from: {pdf_url[:100]}...")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/pdf,application/octet-stream,*/*",
            }

            response = requests.get(pdf_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            content = response.content
            if not content:
                raise ValueError("Downloaded PDF file is empty")

            # Basic PDF validation
            if not content.startswith(b"%PDF"):
                logger.warning("Downloaded content may not be a valid PDF file")

            logger.info(f"Successfully downloaded PDF ({len(content)} bytes)")
            return content

        except requests.RequestException as e:
            logger.error(f"Failed to download PDF from {pdf_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {e}")
            raise ValueError(f"Failed to download PDF: {e}")

    def _load_pdf_content(self, pdf_content: bytes) -> list[Document]:
        """
        Load the PDF content using PyPDFLoader.

        Args:
            pdf_content: The PDF file content as bytes

        Returns:
            list[Document]: List of documents extracted from the PDF

        Raises:
            Exception: If PDF loading fails
        """
        temp_file = None
        try:
            logger.info("Creating temporary PDF file for processing")

            # Create a temporary file with .pdf extension
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            logger.info(f"Temporary PDF file created: {temp_file_path}")

            # Load the PDF using PyPDFLoader
            loader = PyPDFLoader(temp_file_path)
            documents = loader.load()

            if not documents:
                raise ValueError("No content could be extracted from the PDF")

            # Enhance metadata
            for doc in documents:
                doc.metadata.update(
                    {
                        "source": self.url,
                        "loader": "AdobeAcrobatLoader",
                        "original_source": "Adobe Acrobat Share",
                        "file_size": len(pdf_content),
                    }
                )

            logger.info(f"Successfully loaded {len(documents)} document pages from PDF")
            return documents

        except Exception as e:
            logger.error(f"Failed to load PDF content: {e}")
            raise
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    logger.info("Temporary PDF file cleaned up")
                except Exception as e:
                    logger.warning(
                        f"Failed to clean up temporary file {temp_file_path}: {e}"
                    )

    def load(self) -> list[Document]:
        """
        Load documents from the Adobe Acrobat share URL.

        Returns:
            list[Document]: List of documents extracted from the PDF

        Raises:
            Exception: If any step in the loading process fails
        """
        try:
            logger.info("Starting Adobe Acrobat document loading process")

            # Step 1: Fetch the HTML page
            html_content = self._fetch_page_html()

            # Step 2: Extract PDF download URL
            pdf_url = self._extract_pdf_url(html_content)

            # Step 3: Download the PDF
            pdf_content = self._download_pdf(pdf_url)

            # Step 4: Load PDF content
            documents = self._load_pdf_content(pdf_content)

            logger.info("Successfully completed Adobe Acrobat loading process")
            return documents

        except Exception as e:
            logger.error(f"Adobe Acrobat loading failed: {e}")
            raise ValueError(f"Failed to load document from Adobe Acrobat: {e}")

    async def aload(self) -> list[Document]:
        """
        Async version of load method.

        Note: Currently just calls the sync version.
        Could be improved with aiohttp for async HTTP requests.

        Returns:
            list[Document]: List of documents extracted from the PDF
        """
        return self.load()
