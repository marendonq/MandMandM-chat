from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.file import FileEntity

class FileRepository(ABC):

    @abstractmethod
    def save(self, file: FileEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, file_id: str) -> Optional[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    def get_by_message_id(self, message_id: str) -> List[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    def find_by_uploader_id(self, uploader_id: str) -> List[FileEntity]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, file_id: str) -> None:
        raise NotImplementedError