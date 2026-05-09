from abc import ABC, abstractmethod

class FileStorage(ABC):
    """Abstract port for file storage operations.

    Defines the contract for uploading, deleting, and generating URLs
    for stored files. Implementations can use local filesystem, S3,
    or other cloud storage providers.
    """

    @abstractmethod
    def upload(self, file_bytes: bytes, file_name: str) -> str:
        """Upload file content to the storage backend.

        Args:
            file_bytes: The raw file content to upload.
            file_name: The filename to store the content under.

        Returns:
            The storage path or key where the file was saved.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        """Delete a file from the storage backend.

        Args:
            storage_path: The storage path or key of the file to delete.
        """
        raise NotImplementedError

    @abstractmethod
    def get_url(self, storage_path: str) -> str:
        """Generate a URL for accessing a stored file.

        Args:
            storage_path: The storage path or key of the file.

        Returns:
            A URL string for accessing the file.
        """
        raise NotImplementedError