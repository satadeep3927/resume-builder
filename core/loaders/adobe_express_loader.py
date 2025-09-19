import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator

import aiohttp
import requests
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document

# Constants
ADOBE_TOKEN_URL = "https://adobeid-na1.services.adobe.com/ims/check/v6/token?jslVersion=v2-v0.45.0-5-gb993c08"
ADOBE_DOC_URL_TEMPLATE = "https://new.express.adobe.com/service/das/documents/urn:aaid:sc:AP:{urn}?allowArtifact=true"
CLIENT_ID = "projectx_webapp"
SCOPE = "ab.manage,AdobeID,openid,read_organizations,creative_cloud,creative_sdk,tk_platform,tk_platform_sync,af_byof,stk.a.license_skip.r,stk.a.limited_license.cru,additional_info.optionalAgreements,uds_read,uds_write,af_ltd_projectx,unified_dev_portal,additional_info.ownerOrg,additional_info.roles,additional_info.roles,DCAPI,additional_info.auth_source,additional_info.authenticatingAccount,pps.write,pps.delete,pps.image_write,tk_platform_grant_free_subscription,pps.read,firefly_api,additional_info.projectedProductContext,adobeio.appregistry.read,adobeio.appregistry.write,account_cluster.read,indesign_services,eduprofile.write,eduprofile.read"
URN_PREFIX = "urn:aaid:sc:AP:"
REQUEST_TIMEOUT = 10


class AdobeExpressLoader(BaseLoader):
    """Loader that fetches and loads documents from Adobe Express URLs.

    Args:
        url: The Adobe Express URL to load the document from.
        api_key: Your Adobe API key for authentication.
    """

    def __init__(self, url: str):
        if (
            not isinstance(url, str)
            or not url.startswith("https://")
            or URN_PREFIX not in url
        ):
            raise ValueError(
                f"Invalid Adobe Express URL. Must be a string starting with https:// and containing '{URN_PREFIX}'."
            )
        self.url = url

    def _extract_urn(self) -> str:
        """Extract the URN identifier from the Adobe Express URL."""
        if URN_PREFIX in self.url:
            return self.url.split(URN_PREFIX)[1].split("?")[0]
        else:
            raise ValueError("Invalid Adobe Express URL format.")

    def extract_text_models(self, doc_model: Dict[str, Any]) -> list[str]:
        """Extract all TextModel text using BFS to handle deep nesting efficiently."""
        results: list[str] = []
        queue = [doc_model]
        while queue:
            current = queue.pop(0)
            if isinstance(current, dict):
                for k, v in current.items():
                    if isinstance(v, dict):
                        if "TextModel" in v and isinstance(v["TextModel"], dict):
                            text = v["TextModel"].get("text")
                            if text:
                                results.append(text)
                        queue.append(v)
        return results

    def _fetch_document(self, urn: str, token: str) -> list[str]:
        """Fetch the document data from Adobe Express API and extract text models."""
        headers = {
            "Authorization": f"Bearer {token}",
        }
        api_url = ADOBE_DOC_URL_TEMPLATE.format(urn=urn)
        try:
            response = requests.get(api_url, headers=headers, timeout=REQUEST_TIMEOUT)
            if response.status_code == 401:  # Unauthorized, try without auth
                logging.info("Token auth failed, trying without authentication...")
                response = requests.get(api_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            doc_model = json.loads(data.get("docModel"))
            return self.extract_text_models(doc_model)
        except requests.RequestException as e:
            logging.error(f"Failed to fetch document from {api_url}: {e}")
            raise

    async def _afetch_document(self, urn: str, token: str) -> list[str]:
        """Asynchronously fetch the document data from Adobe Express API and extract text models."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        api_url = ADOBE_DOC_URL_TEMPLATE.format(urn=urn)
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            try:
                async with session.get(api_url, headers=headers) as response:
                    if (
                        response.status == 401 and token
                    ):  # Unauthorized with token, try without
                        logging.info(
                            "Token auth failed, trying without authentication..."
                        )
                        async with session.get(api_url) as response:
                            response.raise_for_status()
                            data = await response.json()
                    else:
                        response.raise_for_status()
                        data = await response.json()
                        doc_model = json.loads(data.get("docModel"))
                    return self.extract_text_models(doc_model)
            except aiohttp.ClientError as e:
                logging.error(
                    f"Failed to fetch document asynchronously from {api_url}: {e}"
                )
                raise

    def _get_oauth_token(self) -> str:
        """Obtain an OAuth access token for Adobe Express API authentication."""
        payload = {
            "guest_allowed": "true",
            "client_id": CLIENT_ID,
            "scope": SCOPE,
        }

        headers = {
            "referer": "https://new.express.adobe.com/",
            "origin": "https://new.express.adobe.com",
        }
        try:
            response = requests.post(
                ADOBE_TOKEN_URL, headers=headers, data=payload, timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]
        except requests.RequestException as e:
            logging.error(f"Failed to obtain OAuth token: {e}")
            raise

    async def _aget_oauth_token(self) -> str:
        """Asynchronously obtain an OAuth access token for Adobe Express API authentication."""
        payload = {
            "guest_allowed": "true",
            "client_id": CLIENT_ID,
            "scope": SCOPE,
        }

        headers = {
            "referer": "https://new.express.adobe.com/",
            "origin": "https://new.express.adobe.com",
        }
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            try:
                async with session.post(
                    ADOBE_TOKEN_URL, headers=headers, data=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data["access_token"]
            except aiohttp.ClientError as e:
                logging.error(f"Failed to obtain OAuth token asynchronously: {e}")
                raise

    def load(self) -> list[Document]:
        """Load the document from the Adobe Express URL."""
        urn = self._extract_urn()
        try:
            token = self._get_oauth_token()
            texts = self._fetch_document(urn, token)
        except Exception as e:
            logging.warning(f"OAuth failed ({e}), trying without authentication...")
            texts = self._fetch_document(
                urn, ""
            )  # Empty token will trigger no-auth path
        documents = [
            Document(page_content=text, metadata={"source": self.url}) for text in texts
        ]
        return documents

    def lazy_load(self) -> Iterator[Document]:
        """Lazy load documents, yielding one at a time."""
        urn = self._extract_urn()
        try:
            token = self._get_oauth_token()
            texts = self._fetch_document(urn, token)
        except Exception as e:
            logging.warning(f"OAuth failed ({e}), trying without authentication...")
            texts = self._fetch_document(urn, "")
        for text in texts:
            yield Document(page_content=text, metadata={"source": self.url})

    async def aload(self) -> AsyncIterator[Document]:
        """Asynchronously load documents, yielding one at a time."""
        urn = self._extract_urn()
        try:
            token = await self._aget_oauth_token()
            texts = await self._afetch_document(urn, token)
        except Exception as e:
            logging.warning(f"OAuth failed ({e}), trying without authentication...")
            texts = await self._afetch_document(urn, "")
        for text in texts:
            yield Document(page_content=text, metadata={"source": self.url})
