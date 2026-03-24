from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.file import File

class FileRepositiory(ABC):

    @abstractmethod
    def save(self, file: File) -> None:
        pass

    @abstractmethod
    def find_by_id(self, file_id: str) -> Optional[File]:
        pass

    