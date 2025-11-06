from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel


class AssetURLs(BaseModel):
    url: str
    download_url: str


class File(BaseModel):
    assetURLs: AssetURLs


class Data(BaseModel):
    file: File


class Acrobat(BaseModel):
    data: Data
    ui: Dict[str, Any]

    model_config = {"extra": "allow"}
