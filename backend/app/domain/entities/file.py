from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
import os


class FileType(str, Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"

    @property
    def is_image(self) -> bool:
        return self == FileType.IMAGE

class FileEntity:

    def __init__(
            self,
            id: str,
            file_name: str,
            file_type: FileType,
            uploader_id: str,
            storage_path: str,
            created_at: datetime,
            file_size: Optional[int] = None,
            message_id: Optional[str] = None,
            thumbnail_path: Optional[str] = None
        ):

            self._validate_file_name(file_name)

            self._validate_file_type(file_type)

            self._validate_storage_path(storage_path)

            if thumbnail_path:
                self._validate_thumbnail(thumbnail_path, file_type)

            self._validate_id(id)

            self._validate_uploader_id(uploader_id)

            self.id = id
            self.uploader_id = uploader_id
            self.message_id = message_id
            self.file_name = file_name
            self.file_type = file_type
            self.file_size = file_size
            self.storage_path = storage_path
            self.thumbnail_path = thumbnail_path
            self.created_at =  created_at

    # Validations funtions

    @staticmethod
    def _validate_id(id: str):
        if not id:
            raise ValueError("File id is required")

    @staticmethod
    def _validate_file_name(file_name: str):
        if not file_name or not file_name.strip():
            raise ValueError("File name is required")

        if len(file_name) > 255:
            raise ValueError("File name too long")

    @staticmethod
    def _validate_file_type(file_type):
        if file_type is None:
            raise ValueError("File type is required")

    @staticmethod
    def _validate_uploader_id(uploader_id: str):
        if not uploader_id:
            raise ValueError("Uploader id is required")

    @staticmethod
    def _validate_storage_path(storage_path: str):
        if not storage_path or not storage_path.strip():
            raise ValueError("Storage path is required")

    @staticmethod
    def _validate_thumbnail(thumbnail_path: Optional[str], file_type):

        if thumbnail_path and not file_type.is_image:
            raise ValueError("Only image files can have a thumbnail")


class FileEntityFactory:

    @staticmethod
    def create(
        id: Optional[str],
        file_name: str,
        file_type: "FileType",
        uploader_id: str,
        storage_path: str,
        file_size: Optional[int] = None,
        message_id: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> FileEntity:

        file_id = id or str(uuid.uuid4())

        return FileEntity(
            id=file_id,
            file_name=file_name,
            file_type=file_type,
            uploader_id=uploader_id,
            storage_path=storage_path,
            created_at=created_at or datetime.utcnow(),
            file_size=file_size,
            message_id=message_id,
            thumbnail_path=thumbnail_path
        )