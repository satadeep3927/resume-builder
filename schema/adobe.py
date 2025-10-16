from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel


class RenditionImage(BaseModel):
    rendered: bool


class Lpm(BaseModel):
    shouldRenderLpmThroughEW: bool
    renditionImages: List[RenditionImage]


class AssetURLs(BaseModel):
    url: str
    download_url: str


class File(BaseModel):
    shouldFetchBootstrapDataFromEW: bool
    shouldEnableOpenPDFCaching: bool
    shouldEnableFirstAjsPageCaching: bool
    shouldEnableLpm: bool
    lpm: Lpm
    enableMetaDataAndRenditionAPI: bool
    assetURLs: AssetURLs


class Data(BaseModel):
    file: File


class Acrobat(BaseModel):
    data: Data
    ui: Dict[str, Any]
