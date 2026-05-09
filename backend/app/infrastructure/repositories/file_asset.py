"""In-memory implementation of the FileAssetRepository for testing/development.

This repository stores file asset metadata in memory using a list of dictionaries.
It is not suitable for production use but provides a simple implementation
for testing and development purposes.
"""

from copy import copy

from app.domain.entities.file_asset import FileAssetEntity
from app.domain.repositories.file_asset import FileAssetRepository


class FileAssetInMemoryRepository(FileAssetRepository):
    """In-memory repository for FileAssetEntity.

    Stores file asset data in a list of dictionaries. Useful for testing
    and development without requiring a database connection.
    """

    def __init__(self):
        """Initialize an empty in-memory store."""
        self._store: list[dict] = []

    def add(self, asset: FileAssetEntity) -> FileAssetEntity:
        """Persist a new file asset entity.

        Args:
            asset: The FileAssetEntity to persist.

        Returns:
            The persisted FileAssetEntity.
        """
        self._store.append(copy(self._to_row(asset)))
        return asset

    def get_by_id(self, asset_id: str) -> FileAssetEntity | None:
        """Retrieve a file asset by its ID.

        Args:
            asset_id: The unique file asset identifier.

        Returns:
            The FileAssetEntity if found, otherwise None.
        """
        for row in self._store:
            if row["id"] == asset_id:
                return self._to_entity(row)
        return None

    def list_by_owner(self, owner_profile_id: str) -> list[FileAssetEntity]:
        """List all file assets owned by a specific user profile.

        Args:
            owner_profile_id: The ID of the user profile to query.

        Returns:
            A list of FileAssetEntity objects owned by the user.
        """
        return [self._to_entity(r) for r in self._store if r["owner_profile_id"] == owner_profile_id]

    def delete(self, asset_id: str) -> None:
        """Delete a file asset by its ID.

        Args:
            asset_id: The unique file asset identifier to delete.
        """
        self._store = [r for r in self._store if r["id"] != asset_id]

    @staticmethod
    def _to_row(a: FileAssetEntity) -> dict:
        """Convert a FileAssetEntity to a dictionary for storage.

        Args:
            a: The FileAssetEntity to convert.

        Returns:
            A dictionary representation of the file asset.
        """
        return {
            "id": a.id,
            "owner_profile_id": a.owner_profile_id,
            "original_name": a.original_name,
            "mime_type": a.mime_type,
            "size_bytes": a.size_bytes,
            "storage_key": a.storage_key,
            "created_at": a.created_at,
        }

    @staticmethod
    def _to_entity(row: dict) -> FileAssetEntity:
        """Convert a storage dictionary row to a FileAssetEntity.

        Args:
            row: Dictionary containing file asset data.

        Returns:
            A FileAssetEntity constructed from the row data.
        """
        return FileAssetEntity(
            id=row["id"],
            owner_profile_id=row["owner_profile_id"],
            original_name=row["original_name"],
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            storage_key=row["storage_key"],
            created_at=row["created_at"],
        )
