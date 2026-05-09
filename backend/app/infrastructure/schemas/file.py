"""Pydantic schemas for the file microservice.

Defines request and response models for file upload, retrieval,
and deletion endpoints.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileResponse(BaseModel):
    """Response schema for file metadata.

    Attributes:
        id: Unique file identifier.
        file_name: Original filename as uploaded.
        file_type: The type/category of the file.
        uploader_id: ID of the user who uploaded the file.
        storage_path: Path where the file is stored.
        created_at: Timestamp of file creation.
        file_size: Size of the file in bytes.
        message_id: ID of the associated message.
        thumbnail_path: Optional path to a thumbnail.
    """
    id: str
    file_name: str
    file_type: str
    uploader_id: str
    storage_path: str
    created_at: datetime
    file_size: Optional[int] = None
    message_id: Optional[str] = None
    thumbnail_path: Optional[str] = None


class FileUploadRequest(BaseModel):
    """Request schema for file upload metadata.

    Attributes:
        file_name: Original filename.
        file_type: The type/category of the file.
        uploader_id: ID of the user uploading.
        message_id: ID of the associated message.
    """
    file_name: str
    file_type: str
    uploader_id: str
    message_id: str


class FileDeleteRequest(BaseModel):
    """Request schema for file deletion.

    Attributes:
        file_id: The unique file identifier to delete.
    """
    file_id: str