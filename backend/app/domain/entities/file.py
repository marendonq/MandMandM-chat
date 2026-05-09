from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
import os


class FileType(str, Enum):
    """Enumeration of supported file types.

    Attributes:
        IMAGE: Image file (e.g., PNG, JPEG, GIF).
        DOCUMENT: Document file (e.g., PDF, DOCX, TXT).
        VIDEO: Video file (e.g., MP4, AVI, MOV).
    """
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"

    @property
    def is_image(self) -> bool:
        """Check if this file type is an image.

        Returns:
            True if the file type is IMAGE, False otherwise.
        """
        return self == FileType.IMAGE


class FileEntity:
    """Domain entity representing a file associated with a message.

    Encapsulates file metadata including the original filename, type,
    uploader information, and storage location. Validates all required
    fields at construction time.
    """

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
        """Initialize a file entity.

        Args:
            id: Unique identifier for the file.
            file_name: Original filename as uploaded.
            file_type: The type/category of the file.
            uploader_id: ID of the user who uploaded the file.
            storage_path: Path where the file is stored in the storage backend.
            created_at: Timestamp of file creation.
            file_size: Size of the file in bytes.
            message_id: ID of the message this file is associated with.
            thumbnail_path: Optional path to a thumbnail (images only).

        Raises:
            ValueError: If any required field is missing or invalid.
        """
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
        self.created_at = created_at

    # Validation methods

    @staticmethod
    def _validate_id(id: str):
        """Validate that the file ID is present.

        Args:
            id: The file ID to validate.

        Raises:
            ValueError: If id is empty.
        """
        if not id:
            raise ValueError("File id is required")

    @staticmethod
    def _validate_file_name(file_name: str):
        """Validate the filename format and length.

        Args:
            file_name: The filename to validate.

        Raises:
            ValueError: If filename is empty or exceeds 255 characters.
        """
        if not file_name or not file_name.strip():
            raise ValueError("File name is required")

        if len(file_name) > 255:
            raise ValueError("File name too long")

    @staticmethod
    def _validate_file_type(file_type):
        """Validate that the file type is specified.

        Args:
            file_type: The file type to validate.

        Raises:
            ValueError: If file_type is None.
        """
        if file_type is None:
            raise ValueError("File type is required")

    @staticmethod
    def _validate_uploader_id(uploader_id: str):
        """Validate that the uploader ID is present.

        Args:
            uploader_id: The uploader ID to validate.

        Raises:
            ValueError: If uploader_id is empty.
        """
        if not uploader_id:
            raise ValueError("Uploader id is required")

    @staticmethod
    def _validate_storage_path(storage_path: str):
        """Validate that the storage path is present.

        Args:
            storage_path: The storage path to validate.

        Raises:
            ValueError: If storage_path is empty.
        """
        if not storage_path or not storage_path.strip():
            raise ValueError("Storage path is required")

    @staticmethod
    def _validate_thumbnail(thumbnail_path: Optional[str], file_type):
        """Validate thumbnail constraints.

        Only image files are allowed to have thumbnails.

        Args:
            thumbnail_path: The thumbnail path to validate.
            file_type: The file type of the file.

        Raises:
            ValueError: If a non-image file has a thumbnail.
        """
        if thumbnail_path and not file_type.is_image:
            raise ValueError("Only image files can have a thumbnail")


class FileEntityFactory:
    """Factory for creating FileEntity instances.

    Provides a consistent way to construct file entities with
    automatic UUID and timestamp generation when not provided.
    """

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
        """Create a new FileEntity.

        Args:
            id: Optional unique identifier. Generated automatically if None.
            file_name: Original filename as uploaded.
            file_type: The type/category of the file.
            uploader_id: ID of the user who uploaded the file.
            storage_path: Path where the file is stored.
            file_size: Optional size of the file in bytes.
            message_id: Optional message ID association.
            thumbnail_path: Optional thumbnail path (images only).
            created_at: Optional creation timestamp. Defaults to now.

        Returns:
            A new FileEntity instance.
        """
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