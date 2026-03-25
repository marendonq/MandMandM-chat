from abc import ABC, abstractmethod

from app.domain.entities.file_asset import FileAssetEntity


class FileAssetRepository(ABC):
    @abstractmethod
    def add(self, asset: FileAssetEntity) -> FileAssetEntity:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, asset_id: str) -> FileAssetEntity | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_owner(self, owner_profile_id: str) -> list[FileAssetEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, asset_id: str) -> None:
        raise NotImplementedError
