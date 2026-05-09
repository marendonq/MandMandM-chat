from abc import ABC, abstractmethod

from app.domain.entities.file_asset import FileAssetEntity


class FileAssetRepository(ABC):
    """Abstract repository for FileAssetEntity persistence operations.

    Defines the contract for storing and retrieving file asset metadata
    including ownership-based queries.
    """

    @abstractmethod
    def add(self, asset: FileAssetEntity) -> FileAssetEntity:
        """Persist a new file asset entity.

        Args:
            asset: The FileAssetEntity to persist.

        Returns:
            The persisted FileAssetEntity.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, asset_id: str) -> FileAssetEntity | None:
        """Retrieve a file asset by its ID.

        Args:
            asset_id: The unique file asset identifier.

        Returns:
            The FileAssetEntity if found, otherwise None.
        """
        raise NotImplementedError

    @abstractmethod
    def list_by_owner(self, owner_profile_id: str) -> list[FileAssetEntity]:
        """List all file assets owned by a specific user profile.

        Args:
            owner_profile_id: The ID of the user profile to query.

        Returns:
            A list of FileAssetEntity objects owned by the user.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, asset_id: str) -> None:
        """Delete a file asset by its ID.

        Args:
            asset_id: The unique file asset identifier to delete.
        """
        raise NotImplementedError
