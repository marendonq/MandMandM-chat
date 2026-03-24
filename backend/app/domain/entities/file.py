from datetime import datetime 
from typing import Optional

class File:
    
    def __init__(
            self,
            id: str,
            file_name: str,
            uploader_id: str, 
            file_type: str, 
            storage_path: str,
            created_at: datetime,
            file_size: Optional[int] = None,
            message_id: Optional[str] = None,
            thumbnail_path: Optional[str] = None
        ):
            if not file_name:
                    raise ValueError("file_name is required")

            if not file_type:
                raise ValueError("file_type is required")

            if not storage_path:
                raise ValueError("storage_path is required")

            self.id = id
            self.uploader_id = uploader_id
            self.message_id = message_id
            self.file_name = file_name 
            self.file_type = file_type
            self.file_size = file_size
            self.storage_path = storage_path
            self.thumbnail_path = thumbnail_path
            self.created_at =  created_at