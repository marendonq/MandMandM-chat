from copy import copy
from typing import Optional, List
from app.domain.entities.file import FileEntity
from app.domain.repositories.file import FileRepository


class FileInMemoryRepository(FileRepository):
    def __init__(self):
        self._store: List[dict] = []

    def save(self, file: FileEntity) -> None:
        self._store.append(copy(self._entity_to_row(file)))

    def get_by_id(self, file_id: str) -> Optional[FileEntity]:
        for row in self._store:
            if row["id"] == file_id:
                return self._row_to_entity(row)
        return None

    def get_by_message_id(self, message_id: str) -> List[FileEntity]:
        return [
            self._row_to_entity(row)
            for row in self._store
            if row["message_id"] == message_id
        ]

    def find_by_uploader_id(self, uploader_id: str) -> List[FileEntity]:
        return [
            self._row_to_entity(row)
            for row in self._store
            if row["uploader_id"] == uploader_id
        ]

    def delete(self, file_id: str) -> None:
        self._store = [row for row in self._store if row["id"] != file_id]

    @staticmethod
    def _entity_to_row(file: FileEntity) -> dict:
        return {
            "id": file.id,
            "file_name": file.file_name,
            "file_type": file.file_type.value if hasattr(file.file_type, 'value') else file.file_type,
            "uploader_id": file.uploader_id,
            "storage_path": file.storage_path,
            "created_at": file.created_at,
            "file_size": file.file_size,
            "message_id": file.message_id,
            "thumbnail_path": file.thumbnail_path,
        }

    @staticmethod
    def _row_to_entity(row: dict) -> FileEntity:
        from app.domain.entities.file import FileType
        return FileEntity(
            id=row["id"],
            file_name=row["file_name"],
            file_type=FileType(row["file_type"]),
            uploader_id=row["uploader_id"],
            storage_path=row["storage_path"],
            created_at=row["created_at"],
            file_size=row.get("file_size"),
            message_id=row.get("message_id"),
            thumbnail_path=row.get("thumbnail_path"),
        )