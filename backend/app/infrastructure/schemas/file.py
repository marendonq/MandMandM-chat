from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileResponse(BaseModel):
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
    file_name: str
    file_type: str
    uploader_id: str
    message_id: str


class FileDeleteRequest(BaseModel):
    file_id: str