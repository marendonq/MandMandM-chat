from app.domain.entities.file_asset import FileAssetEntityFactory
from app.domain.exceptions import FileAssetNotFound
from app.domain.repositories.file_asset import FileAssetRepository


class FileAssetService:
    """Service for managing file assets and their metadata.

    File assets represent files stored in the system with associated
    metadata such as owner, original name, MIME type, and size.
    """

    def __init__(self, repository: FileAssetRepository):
        """Initialize the file asset service.

        Args:
            repository: Repository for file asset persistence.
        """
        self._repo = repository

    def register_metadata(
        self,
        owner_profile_id: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        storage_key: str,
    ):
        """Register metadata for a newly uploaded file asset.

        Creates a new file asset entity with the provided metadata
        and persists it to the repository.

        Args:
            owner_profile_id: ID of the user profile that owns this file.
            original_name: The original filename as uploaded.
            mime_type: The MIME type of the file content.
            size_bytes: The size of the file in bytes.
            storage_key: The key/path used to locate the file in storage.

        Returns:
            The created FileAssetEntity.
        """
        entity = FileAssetEntityFactory.create(
            owner_profile_id, original_name, mime_type, size_bytes, storage_key
        )
        return self._repo.add(entity)

    def get(self, asset_id: str):
        """Retrieve a file asset by its ID.

        Args:
            asset_id: The unique identifier of the file asset.

        Returns:
            The FileAssetEntity if found.

        Raises:
            FileAssetNotFound: If no file asset exists with the given ID.
        """
        found = self._repo.get_by_id(asset_id)
        if found is None:
            raise FileAssetNotFound()
        return found

    def list_by_owner(self, owner_profile_id: str):
        """List all file assets owned by a specific user profile.

        Args:
            owner_profile_id: The ID of the user profile to query.

        Returns:
            A list of FileAssetEntity objects owned by the user.
        """
        return self._repo.list_by_owner(owner_profile_id)

    def delete(self, asset_id: str) -> None:
        """Delete a file asset by its ID.

        Args:
            asset_id: The unique identifier of the file asset to delete.

        Raises:
            FileAssetNotFound: If no file asset exists with the given ID.
        """
        self.get(asset_id)
        self._repo.delete(asset_id)
