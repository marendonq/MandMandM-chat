"""PostgreSQL implementation of the FileAssetRepository.

This module provides a production-ready repository for file asset metadata
using SQLAlchemy with PostgreSQL.
"""

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.file_asset import FileAssetEntity
from app.domain.repositories.file_asset import FileAssetRepository
from app.infrastructure.database.models import FileAssetModel


class FileAssetPostgresRepository(FileAssetRepository):
    """PostgreSQL repository for FileAssetEntity.

    Uses SQLAlchemy ORM to persist file asset metadata in PostgreSQL.
    """

    def __init__(self, session_factory: sessionmaker):
        """Initialize the PostgreSQL file asset repository.

        Args:
            session_factory: SQLAlchemy session factory for database access.
        """
        self._sf = session_factory

    def _session(self) -> Session:
        """Create a new database session.

        Returns:
            A new SQLAlchemy Session.
        """
        return self._sf()

    @staticmethod
    def _to_entity(row: FileAssetModel) -> FileAssetEntity:
        """Convert a database model to a FileAssetEntity.

        Args:
            row: The FileAssetModel from the database.

        Returns:
            A FileAssetEntity constructed from the model data.
        """
        return FileAssetEntity(
            id=row.id,
            owner_profile_id=row.owner_profile_id,
            original_name=row.original_name,
            mime_type=row.mime_type,
            size_bytes=row.size_bytes,
            storage_key=row.storage_key,
            created_at=row.created_at,
        )

    def add(self, asset: FileAssetEntity) -> FileAssetEntity:
        """Persist a new file asset entity to PostgreSQL.

        Args:
            asset: The FileAssetEntity to persist.

        Returns:
            The persisted FileAssetEntity.
        """
        with self._session() as s:
            s.add(
                FileAssetModel(
                    id=asset.id,
                    owner_profile_id=asset.owner_profile_id,
                    original_name=asset.original_name,
                    mime_type=asset.mime_type,
                    size_bytes=asset.size_bytes,
                    storage_key=asset.storage_key,
                    created_at=asset.created_at,
                )
            )
            s.commit()
        return asset

    def get_by_id(self, asset_id: str) -> FileAssetEntity | None:
        """Retrieve a file asset by its ID from PostgreSQL.

        Args:
            asset_id: The unique file asset identifier.

        Returns:
            The FileAssetEntity if found, otherwise None.
        """
        with self._session() as s:
            row = s.get(FileAssetModel, asset_id)
            if row is None:
                return None
            return self._to_entity(row)

    def list_by_owner(self, owner_profile_id: str) -> list[FileAssetEntity]:
        """List all file assets owned by a specific user profile.

        Args:
            owner_profile_id: The ID of the user profile to query.

        Returns:
            A list of FileAssetEntity objects owned by the user.
        """
        with self._session() as s:
            rows = s.scalars(
                select(FileAssetModel).where(FileAssetModel.owner_profile_id == owner_profile_id)
            ).all()
            return [self._to_entity(r) for r in rows]

    def delete(self, asset_id: str) -> None:
        """Delete a file asset from PostgreSQL by its ID.

        Args:
            asset_id: The unique file asset identifier to delete.
        """
        with self._session() as s:
            row = s.get(FileAssetModel, asset_id)
            if row is not None:
                s.delete(row)
            s.commit()
