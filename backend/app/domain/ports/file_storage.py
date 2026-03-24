from abc import ABC, abstractmethod

class FileStorage(ABC):

    @abstractmethod
    def upload(self, file_bytes: bytes, file_name: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def delete(self, storage_path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_url(self, storage_path: str) -> str:
        raise NotImplementedError