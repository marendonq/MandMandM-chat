from datetime import datetime

from pydantic import BaseModel, Field


class FileAssetRegisterRequest(BaseModel):
    owner_profile_id: str = Field(..., min_length=1)
    original_name: str = Field(..., min_length=1)
    mime_type: str = ""
    size_bytes: int = Field(..., ge=0)
    storage_key: str = Field(..., min_length=1)


class FileAssetResponse(BaseModel):
    id: str
    owner_profile_id: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_key: str
    created_at: datetime


class FileAssetListResponse(BaseModel):
    items: list[FileAssetResponse]
