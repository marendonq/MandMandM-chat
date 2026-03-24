from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.file import FileEntity, FileType


class UploadFileUseCase(ABC):

    @abstractmethod
    def execute(
        self,
        file_bytes: bytes,
        file_name: str,
        file_type: FileType,
        uploader_id: str,
        message_id: str,
        thumbnail_path: Optional[str] = None
    ) -> FileEntity:
        pass


class GetFileUseCase(ABC):

    @abstractmethod
    def execute(self, file_id: str) -> FileEntity:
        pass


class GetFilesByMessageUseCase(ABC):

    @abstractmethod
    def execute(self, message_id: str) -> list[FileEntity]:
        pass


class DeleteFileUseCase(ABC):

    @abstractmethod
    def execute(self, file_id: str) -> None:
        pass