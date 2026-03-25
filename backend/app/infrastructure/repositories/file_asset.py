from copy import copy

from app.domain.entities.file_asset import FileAssetEntity
from app.domain.repositories.file_asset import FileAssetRepository


class FileAssetInMemoryRepository(FileAssetRepository):
    def __init__(self):
        self._store: list[dict] = []

    def add(self, asset: FileAssetEntity) -> FileAssetEntity:
        self._store.append(copy(self._to_row(asset)))
        return asset

    def get_by_id(self, asset_id: str) -> FileAssetEntity | None:
        for row in self._store:
            if row["id"] == asset_id:
                return self._to_entity(row)
        return None

    def list_by_owner(self, owner_profile_id: str) -> list[FileAssetEntity]:
        return [self._to_entity(r) for r in self._store if r["owner_profile_id"] == owner_profile_id]

    def delete(self, asset_id: str) -> None:
        self._store = [r for r in self._store if r["id"] != asset_id]

    @staticmethod
    def _to_row(a: FileAssetEntity) -> dict:
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
        return FileAssetEntity(
            id=row["id"],
            owner_profile_id=row["owner_profile_id"],
            original_name=row["original_name"],
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            storage_key=row["storage_key"],
            created_at=row["created_at"],
        )
