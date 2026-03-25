from app.domain.entities.file_asset import FileAssetEntityFactory
from app.domain.exceptions import FileAssetNotFound
from app.domain.repositories.file_asset import FileAssetRepository


class FileAssetService:
    def __init__(self, repository: FileAssetRepository):
        self._repo = repository

    def register_metadata(
        self,
        owner_profile_id: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        storage_key: str,
    ):
        entity = FileAssetEntityFactory.create(
            owner_profile_id, original_name, mime_type, size_bytes, storage_key
        )
        return self._repo.add(entity)

    def get(self, asset_id: str):
        found = self._repo.get_by_id(asset_id)
        if found is None:
            raise FileAssetNotFound()
        return found

    def list_by_owner(self, owner_profile_id: str):
        return self._repo.list_by_owner(owner_profile_id)

    def delete(self, asset_id: str) -> None:
        self.get(asset_id)
        self._repo.delete(asset_id)
