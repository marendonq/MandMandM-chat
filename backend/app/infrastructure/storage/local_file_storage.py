import os
from pathlib import Path
from app.domain.ports.file_storage import FileStorage


class LocalFileStorageAdapter(FileStorage):

    def __init__(self, base_path: str = None):
        if base_path is None:
            # Default to a 'uploads' directory in the project root
            base_path = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def upload(self, file_bytes: bytes, file_name: str) -> str:
        """Upload a file to local storage and return the storage path."""
        file_path = self.base_path / file_name

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        # Return relative path from base_path for storage_path
        return str(file_path)

    def delete(self, storage_path: str) -> None:
        """Delete a file from local storage."""
        file_path = Path(storage_path)
        if file_path.exists():
            file_path.unlink()

    def get_url(self, storage_path: str) -> str:
        """Get the URL for a stored file."""
        # For local storage, return the file path
        return storage_path