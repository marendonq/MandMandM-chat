from app.domain.use_cases.file import (
    UploadFileUseCase,
    GetFileUseCase,
    GetFilesByMessageUseCase,
    DeleteFileUseCase,
)

from app.domain.repositories.file import FileRepository
from app.domain.ports.file_storage import FileStorage
from app.domain.entities.file import FileEntity, FileType, FileEntityFactory

import uuid


class UploadFileService(UploadFileUseCase):
    """Service for uploading and storing files associated with messages.

    Handles the complete file upload workflow including validation, storage,
    and metadata persistence.
    """

    def __init__(self, repo: FileRepository, storage: FileStorage):
        """Initialize the upload file service.

        Args:
            repo: Repository for file metadata persistence.
            storage: Storage backend for the actual file content.
        """
        self.repo = repo
        self.storage = storage

    def execute(
        self,
        file_bytes: bytes,
        file_name: str,
        file_type: FileType,
        uploader_id: str,
        message_id: str,
        thumbnail_path: str | None = None
    ) -> FileEntity:
        """Upload a file and persist its metadata.

        Generates a unique filename, uploads the content to storage,
        and saves the file entity metadata.

        Args:
            file_bytes: The raw file content.
            file_name: The original filename.
            file_type: The type/category of the file.
            uploader_id: ID of the user uploading the file.
            message_id: ID of the message this file is associated with.
            thumbnail_path: Optional path to a thumbnail image.

        Returns:
            The created FileEntity with all metadata.

        Raises:
            ValueError: If file_bytes is empty.
        """
        if not file_bytes:
            raise ValueError("File is empty")

        unique_file_name = f"{uuid.uuid4()}_{file_name}"

        storage_path = self.storage.upload(file_bytes, unique_file_name)

        file = FileEntityFactory.create(
            id=None,
            file_name=file_name,
            file_type=file_type,
            uploader_id=uploader_id,
            storage_path=storage_path,
            file_size=len(file_bytes),
            message_id=message_id,
            thumbnail_path=thumbnail_path
        )

        self.repo.save(file)

        return file


class GetFileService(GetFileUseCase):
    """Service for retrieving a single file by its ID."""

    def __init__(self, repo: FileRepository):
        """Initialize the get file service.

        Args:
            repo: Repository for file metadata lookup.
        """
        self.repo = repo

    def execute(self, file_id: str) -> FileEntity:
        """Retrieve a file entity by its ID.

        Args:
            file_id: The unique identifier of the file.

        Returns:
            The FileEntity if found.

        Raises:
            ValueError: If file_id is empty or file is not found.
        """
        if not file_id:
            raise ValueError("file_id is required")

        file = self.repo.get_by_id(file_id)

        if not file:
            raise ValueError("File not found")

        return file


class GetFilesByMessageService(GetFilesByMessageUseCase):
    """Service for retrieving all files associated with a message."""

    def __init__(self, repo: FileRepository):
        """Initialize the get files by message service.

        Args:
            repo: Repository for file metadata lookup.
        """
        self.repo = repo

    def execute(self, message_id: str) -> list[FileEntity]:
        """Retrieve all files associated with a specific message.

        Args:
            message_id: The ID of the message to get files for.

        Returns:
            A list of FileEntity objects associated with the message.

        Raises:
            ValueError: If message_id is empty.
        """
        if not message_id:
            raise ValueError("message_id is required")

        return self.repo.get_by_message_id(message_id)


class DeleteFileService(DeleteFileUseCase):
    """Service for deleting files from both storage and metadata repository."""

    def __init__(self, repo: FileRepository, storage: FileStorage):
        """Initialize the delete file service.

        Args:
            repo: Repository for file metadata deletion.
            storage: Storage backend for actual file deletion.
        """
        self.repo = repo
        self.storage = storage

    def execute(self, file_id: str) -> None:
        """Delete a file from storage and its metadata.

        First deletes the file content from storage, then removes
        the metadata from the repository.

        Args:
            file_id: The unique identifier of the file to delete.

        Raises:
            ValueError: If file_id is empty or file is not found.
        """
        if not file_id:
            raise ValueError("file_id is required")

        file = self.repo.get_by_id(file_id)

        if not file:
            raise ValueError("File not found")

        self.storage.delete(file.storage_path)

        self.repo.delete(file_id)