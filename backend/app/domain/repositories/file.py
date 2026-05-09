from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.file import FileEntity

class FileRepository(ABC):
    """Abstract repository for FileEntity persistence operations.

    Defines the contract for storing and retrieving file metadata
    associated with messages and users.
    """

    @abstractmethod
    def save(self, file: FileEntity) -> None:
        """Persist a new file entity.

        Args:
            file: The FileEntity to persist.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, file_id: str) -> Optional[FileEntity]:
        """Retrieve a file by its ID.

        Args:
            file_id: The unique file identifier.

        Returns:
            The FileEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_message_id(self, message_id: str) -> List[FileEntity]:
        """Retrieve all files associated with a specific message.

        Args:
            message_id: The message ID to query files for.

        Returns:
            A list of FileEntity objects for the message.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_uploader_id(self, uploader_id: str) -> List[FileEntity]:
        """Retrieve all files uploaded by a specific user.

        Args:
            uploader_id: The user ID to query files for.

        Returns:
            A list of FileEntity objects uploaded by the user.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, file_id: str) -> None:
        """Delete a file entity by its ID.

        Args:
            file_id: The unique file identifier to delete.
        """
        raise NotImplementedError