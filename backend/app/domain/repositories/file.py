from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.file import FileEntity

class FileRepositiory(ABC):

    @abstractmethod
    def save(self, file: FileEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, file_id: str) -> Optional[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    def find_by_message_id(self, message_id: str) -> List[FileEntity]:
        raise NotImplementedError

    def find_by_get_uploader_id(self, uploader_id: str) -> List[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    def delate(self, file_id: str) -> None:
        raise NotImplementedError