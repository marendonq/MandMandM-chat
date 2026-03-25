from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass(frozen=True)
class FileAssetEntity:
    id: str
    owner_profile_id: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_key: str
    created_at: datetime


class FileAssetEntityFactory:
    @staticmethod
    def create(
        owner_profile_id: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        storage_key: str,
    ) -> FileAssetEntity:
        return FileAssetEntity(
            id=str(uuid.uuid4()),
            owner_profile_id=owner_profile_id.strip(),
            original_name=original_name.strip(),
            mime_type=mime_type.strip() or "application/octet-stream",
            size_bytes=int(size_bytes),
            storage_key=storage_key.strip(),
            created_at=datetime.utcnow(),
        )
