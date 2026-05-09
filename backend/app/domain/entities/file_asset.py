from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class FileAssetEntity:
    """Domain entity representing a file asset with metadata.

    File assets represent files stored in the system with associated
    ownership, MIME type, and size information. Immutable (frozen dataclass).

    Attributes:
        id: Unique identifier for the file asset.
        owner_profile_id: ID of the user profile that owns this file.
        original_name: The original filename as uploaded.
        mime_type: The MIME type of the file content.
        size_bytes: The size of the file in bytes.
        storage_key: The key/path used to locate the file in storage.
        created_at: Timestamp of file asset creation.
    """
    id: str
    owner_profile_id: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_key: str
    created_at: datetime


class FileAssetEntityFactory:
    """Factory for creating FileAssetEntity instances.

    Provides a consistent way to construct file asset entities with
    automatic UUID and timestamp generation.
    """

    @staticmethod
    def create(
        owner_profile_id: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        storage_key: str,
    ) -> FileAssetEntity:
        """Create a new FileAssetEntity.

        Args:
            owner_profile_id: ID of the user profile that owns this file.
            original_name: The original filename as uploaded.
            mime_type: The MIME type of the file content.
            size_bytes: The size of the file in bytes.
            storage_key: The key/path used to locate the file in storage.

        Returns:
            A new FileAssetEntity with auto-generated ID and timestamp.
        """
        return FileAssetEntity(
            id=str(uuid.uuid4()),
            owner_profile_id=owner_profile_id.strip(),
            original_name=original_name.strip(),
            mime_type=mime_type.strip() or "application/octet-stream",
            size_bytes=int(size_bytes),
            storage_key=storage_key.strip(),
            created_at=datetime.utcnow(),
        )
