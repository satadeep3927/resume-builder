from urllib.parse import quote

import requests
from langchain_community.document_loaders.base import BaseLoader

# Template for Adobe Acrobat page rendering API (corrected based on working example)
ACROBAT_PAGE_URL_TEMPLATE = "https://cdn-sharing.adobecc.com/rendition/id/urn:aaid:sc:AP:{urn};page={page};size=1200;type=image%2Fjpeg?access_token=1759859146_urn%3Aaaid%3Asc%3AAP%3A{encoded_urn}%3Bpublic_fb420c5549b0b42971592fd46283357111fe3e82&api_key=dc_sendtrack"
URN_PREFIX = "urn:aaid:sc:AP:"


class AdobeAcrobatLoader(BaseLoader):
    def __init__(self, url: str):
        if (
            not isinstance(url, str)
            or not url.startswith("https://")
            or URN_PREFIX not in url
        ):
            raise ValueError(
                f"Invalid Adobe Acrobat URL. Must be a string starting with https:// and containing '{URN_PREFIX}'."
            )
        self.url = url

    def _extract_urn(self) -> str:
        """Extract the URN identifier from the Adobe Acrobat URL."""
        if URN_PREFIX in self.url:
            # Extract URN and clean it up
            urn = self.url.split(URN_PREFIX)[1].split("?")[0]
            # Remove any trailing slashes or other URL artifacts
            urn = urn.rstrip("/")
            print(f"Extracted URN: {urn}")  # Debug logging
            return urn
        else:
            raise ValueError("Invalid Adobe Acrobat URL format.")

    def _fetch_page_image(self, urn: str, page: int) -> bytes:
        """Fetch the page image from Adobe Acrobat."""
        # URL encode the URN for the access token (different encoding than the main URN)
        encoded_urn = quote(urn, safe="")

        api_url = ACROBAT_PAGE_URL_TEMPLATE.format(
            urn=urn,  # Raw URN for the main part
            encoded_urn=encoded_urn,  # Encoded URN for access token
            page=page,  # Use page directly (0, 1, 2, etc.)
        )

        print(f"Fetching page {page} with URL: {api_url}")  # Debug logging

        response = requests.get(api_url, timeout=10)

        if response.status_code != 200:
            print(f"HTTP {response.status_code}: {response.text}")  # Debug logging

        response.raise_for_status()  # Will raise an exception for 404 or other errors
        return response.content

    def _fetch_all_pages(self, urn: str) -> list[bytes]:
        """Fetch all page images by iterating until 404."""
        pages = []
        page_num = 0  # Start from page 0

        while True:
            try:
                image_data = self._fetch_page_image(urn, page_num)
                pages.append(image_data)
                page_num += 1
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # No more pages available
                    break
                else:
                    # Other HTTP error, re-raise
                    raise
            except Exception as e:
                # Other error, stop iteration
                print(f"Error fetching page {page_num}: {e}")
                break

        return pages

    def _extract_text_from_image(self, image_data: bytes) -> str:
        """Extract text from image using OCR."""
        try:
            import io

            import pytesseract
            from PIL import Image

            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            return text.strip()

        except ImportError:
            raise ImportError(
                "PIL and pytesseract are required for OCR. "
                "Install with: pip install Pillow pytesseract"
            )
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def load(self):
        """Load and return documents from Adobe Acrobat PDF."""
        from langchain_core.documents import Document

        try:
            # Extract URN from URL
            urn = self._extract_urn()

            # Fetch all page images
            page_images = self._fetch_all_pages(urn)

            if not page_images:
                raise ValueError("No pages found in the document")

            # Extract text from each page
            all_text = []
            for i, image_data in enumerate(page_images, 1):
                page_text = self._extract_text_from_image(image_data)
                if page_text:
                    all_text.append(f"--- Page {i} ---\n{page_text}")

            # Combine all pages into one document
            full_text = "\n\n".join(all_text)

            # Create document with metadata
            document = Document(
                page_content=full_text,
                metadata={
                    "source": self.url,
                    "total_pages": len(page_images),
                    "loader": "AdobeAcrobatLoader",
                },
            )

            return [document]

        except Exception as e:
            raise ValueError(f"Failed to load document from Adobe Acrobat: {str(e)}")
