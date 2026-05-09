from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.file import FileEntity, FileType


class UploadFileUseCase(ABC):
    """Abstract use case for uploading files.

    Defines the contract for the file upload workflow including
    validation, storage, and metadata persistence.
    """

    @abstractmethod
    def execute(
        self,
        file_bytes: bytes,
        file_name: str,
        file_type: FileType,
        uploader_id: str,
        message_id: str,
        thumbnail_path: Optional[str] = None
    ) -> FileEntity:
        """Upload a file and persist its metadata.

        Args:
            file_bytes: The raw file content.
            file_name: The original filename.
            file_type: The type/category of the file.
            uploader_id: ID of the user uploading the file.
            message_id: ID of the message this file is associated with.
            thumbnail_path: Optional path to a thumbnail image.

        Returns:
            The created FileEntity with all metadata.
        """
        pass


class GetFileUseCase(ABC):
    """Abstract use case for retrieving a single file by ID."""

    @abstractmethod
    def execute(self, file_id: str) -> FileEntity:
        """Retrieve a file entity by its ID.

        Args:
            file_id: The unique identifier of the file.

        Returns:
            The FileEntity if found.
        """
        pass


class GetFilesByMessageUseCase(ABC):
    """Abstract use case for retrieving all files associated with a message."""

    @abstractmethod
    def execute(self, message_id: str) -> list[FileEntity]:
        """Retrieve all files associated with a specific message.

        Args:
            message_id: The ID of the message to get files for.

        Returns:
            A list of FileEntity objects associated with the message.
        """
        pass


class DeleteFileUseCase(ABC):
    """Abstract use case for deleting files from storage and metadata."""

    @abstractmethod
    def execute(self, file_id: str) -> None:
        """Delete a file from storage and its metadata.

        Args:
            file_id: The unique identifier of the file to delete.
        """
        pass