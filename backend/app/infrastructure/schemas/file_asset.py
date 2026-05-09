"""Pydantic schemas for the file asset metadata microservice.

Defines request and response models for file asset registration,
retrieval, and listing endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class FileAssetRegisterRequest(BaseModel):
    """Request schema for registering file asset metadata.

    Attributes:
        owner_profile_id: ID of the user profile that owns the file.
        original_name: The original filename as uploaded.
        mime_type: The MIME type of the file content.
        size_bytes: The size of the file in bytes (non-negative).
        storage_key: The key/path used to locate the file in storage.
    """
    owner_profile_id: str = Field(..., min_length=1)
    original_name: str = Field(..., min_length=1)
    mime_type: str = ""
    size_bytes: int = Field(..., ge=0)
    storage_key: str = Field(..., min_length=1)


class FileAssetResponse(BaseModel):
    """Response schema for file asset metadata.

    Attributes:
        id: Unique file asset identifier.
        owner_profile_id: ID of the owning user profile.
        original_name: The original filename.
        mime_type: The MIME type of the file.
        size_bytes: The file size in bytes.
        storage_key: The storage path/key.
        created_at: Timestamp of file asset creation.
    """
    id: str
    owner_profile_id: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_key: str
    created_at: datetime


class FileAssetListResponse(BaseModel):
    """Response schema for listing file assets.

    Attributes:
        items: List of file asset responses.
    """
    items: list[FileAssetResponse]
