from app.domain.use_cases.file import (
    UploadFileUseCase,
    GetFileUseCase,
    GetFilesByMessageUseCase,
    DeleteFileUseCase,
)

from app.domain.repositories.file import FileRepository
from app.domain.ports.file_storage import FileStorage
from app.domain.entities.file import FileEntity, FileType, FileEntityFactory

import uuid


class UploadFileService(UploadFileUseCase):

    def __init__(self, repo: FileRepository, storage: FileStorage):
        self.repo = repo
        self.storage = storage

    def execute(
        self,
        file_bytes: bytes,
        file_name: str,
        file_type: FileType,
        uploader_id: str,
        message_id: str,
        thumbnail_path: str | None = None
    ) -> FileEntity:

        if not file_bytes:
            raise ValueError("File is empty")

        unique_file_name = f"{uuid.uuid4()}_{file_name}"

        storage_path = self.storage.upload(file_bytes, unique_file_name)

        file = FileEntityFactory.create(
            id=None,
            file_name=file_name,
            file_type=file_type,
            uploader_id=uploader_id,
            storage_path=storage_path,
            file_size=len(file_bytes),
            message_id=message_id,
            thumbnail_path=thumbnail_path
        )

        self.repo.save(file)

        return file

class GetFileService(GetFileUseCase):

    def __init__(self, repo: FileRepository):
        self.repo = repo

    def execute(self, file_id: str) -> FileEntity:

        if not file_id:
            raise ValueError("file_id is required")

        file = self.repo.get_by_id(file_id)

        if not file:
            raise ValueError("File not found")

        return file

class GetFilesByMessageService(GetFilesByMessageUseCase):

    def __init__(self, repo: FileRepository):
        self.repo = repo

    def execute(self, message_id: str) -> list[FileEntity]:

        if not message_id:
            raise ValueError("message_id is required")

        return self.repo.get_by_message_id(message_id)

class DeleteFileService(DeleteFileUseCase):

    def __init__(self, repo: FileRepository, storage: FileStorage):
        self.repo = repo
        self.storage = storage

    def execute(self, file_id: str) -> None:

        if not file_id:
            raise ValueError("file_id is required")

        file = self.repo.get_by_id(file_id)

        if not file:
            raise ValueError("File not found")


        self.storage.delete(file.storage_path)

        self.repo.delete(file_id)