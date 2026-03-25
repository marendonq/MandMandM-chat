from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session

from app.domain.entities.file_asset import FileAssetEntity
from app.domain.repositories.file_asset import FileAssetRepository
from app.infrastructure.database.models import FileAssetModel


class FileAssetPostgresRepository(FileAssetRepository):
    def __init__(self, session_factory: sessionmaker):
        self._sf = session_factory

    def _session(self) -> Session:
        return self._sf()

    @staticmethod
    def _to_entity(row: FileAssetModel) -> FileAssetEntity:
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
        with self._session() as s:
            row = s.get(FileAssetModel, asset_id)
            if row is None:
                return None
            return self._to_entity(row)

    def list_by_owner(self, owner_profile_id: str) -> list[FileAssetEntity]:
        with self._session() as s:
            rows = s.scalars(
                select(FileAssetModel).where(FileAssetModel.owner_profile_id == owner_profile_id)
            ).all()
            return [self._to_entity(r) for r in rows]

    def delete(self, asset_id: str) -> None:
        with self._session() as s:
            row = s.get(FileAssetModel, asset_id)
            if row is not None:
                s.delete(row)
            s.commit()
