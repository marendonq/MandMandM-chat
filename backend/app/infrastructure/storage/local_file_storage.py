"""Local filesystem implementation of the FileStorage port.

This module provides a FileStorage adapter that stores files on the
local filesystem. Suitable for development and testing environments.
"""

import os
from pathlib import Path
from app.domain.ports.file_storage import FileStorage


class LocalFileStorageAdapter(FileStorage):
    """Local filesystem adapter for file storage.

    Implements the FileStorage port to store files on the local
    filesystem. Creates the base directory if it doesn't exist.
    """

    def __init__(self, base_path: str = None):
        """Initialize the local file storage.

        Args:
            base_path: The root directory for storing files. Defaults
                to an 'uploads' directory in the project root.
        """
        if base_path is None:
            # Default to a 'uploads' directory in the project root
            base_path = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload(self, file_bytes: bytes, file_name: str) -> str:
        """Upload a file to the local filesystem.

        Writes the file content to the base directory with the
        specified filename.

        Args:
            file_bytes: The raw file content to store.
            file_name: The filename to use for the stored file.

        Returns:
            The absolute path where the file was saved.
        """
        file_path = self.base_path / file_name

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        # Return absolute path for storage_path
        return str(file_path)

    def delete(self, storage_path: str) -> None:
        """Delete a file from the local filesystem.

        Args:
            storage_path: The path of the file to delete.
        """
        file_path = Path(storage_path)
        if file_path.exists():
            file_path.unlink()

    def get_url(self, storage_path: str) -> str:
        """Get the path for a stored file.

        For local storage, returns the file path as-is since there
        is no HTTP URL for local files.

        Args:
            storage_path: The path of the stored file.

        Returns:
            The file path string.
        """
        return storage_path