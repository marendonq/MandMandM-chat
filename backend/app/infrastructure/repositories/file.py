"""In-memory implementation of the FileRepository for testing/development.

This repository stores file data in memory using a list of dictionaries.
It is not suitable for production use but provides a simple implementation
for testing and development purposes.
"""

from copy import copy
from typing import Optional, List
from app.domain.entities.file import FileEntity
from app.domain.repositories.file import FileRepository


class FileInMemoryRepository(FileRepository):
    """In-memory repository for FileEntity.

    Stores file data in a list of dictionaries. Useful for testing
    and development without requiring a database connection.
    """

    def __init__(self):
        """Initialize an empty in-memory store."""
        self._store: List[dict] = []

    def save(self, file: FileEntity) -> None:
        """Persist a new file entity.

        Args:
            file: The FileEntity to persist.
        """
        self._store.append(copy(self._entity_to_row(file)))

    def get_by_id(self, file_id: str) -> Optional[FileEntity]:
        """Retrieve a file by its ID.

        Args:
            file_id: The unique file identifier.

        Returns:
            The FileEntity if found, otherwise None.
        """
        for row in self._store:
            if row["id"] == file_id:
                return self._row_to_entity(row)
        return None

    def get_by_message_id(self, message_id: str) -> List[FileEntity]:
        """Retrieve all files associated with a specific message.

        Args:
            message_id: The message ID to query files for.

        Returns:
            A list of FileEntity objects for the message.
        """
        return [
            self._row_to_entity(row)
            for row in self._store
            if row["message_id"] == message_id
        ]

    def find_by_uploader_id(self, uploader_id: str) -> List[FileEntity]:
        """Retrieve all files uploaded by a specific user.

        Args:
            uploader_id: The user ID to query files for.

        Returns:
            A list of FileEntity objects uploaded by the user.
        """
        return [
            self._row_to_entity(row)
            for row in self._store
            if row["uploader_id"] == uploader_id
        ]

    def delete(self, file_id: str) -> None:
        """Delete a file entity by its ID.

        Args:
            file_id: The unique file identifier to delete.
        """
        self._store = [row for row in self._store if row["id"] != file_id]

    @staticmethod
    def _entity_to_row(file: FileEntity) -> dict:
        """Convert a FileEntity to a dictionary for storage.

        Args:
            file: The FileEntity to convert.

        Returns:
            A dictionary representation of the file.
        """
        return {
            "id": file.id,
            "file_name": file.file_name,
            "file_type": file.file_type.value if hasattr(file.file_type, 'value') else file.file_type,
            "uploader_id": file.uploader_id,
            "storage_path": file.storage_path,
            "created_at": file.created_at,
            "file_size": file.file_size,
            "message_id": file.message_id,
            "thumbnail_path": file.thumbnail_path,
        }

    @staticmethod
    def _row_to_entity(row: dict) -> FileEntity:
        """Convert a storage dictionary row to a FileEntity.

        Args:
            row: Dictionary containing file data.

        Returns:
            A FileEntity constructed from the row data.
        """
        from app.domain.entities.file import FileType
        return FileEntity(
            id=row["id"],
            file_name=row["file_name"],
            file_type=FileType(row["file_type"]),
            uploader_id=row["uploader_id"],
            storage_path=row["storage_path"],
            created_at=row["created_at"],
            file_size=row.get("file_size"),
            message_id=row.get("message_id"),
            thumbnail_path=row.get("thumbnail_path"),
        )