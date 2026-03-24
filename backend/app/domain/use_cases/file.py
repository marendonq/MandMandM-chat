import uuid
from datetime import datetime
from domain.file import File
from domain.file_repository import FileRepositiory

class UploadFileUseCase:

    def __init__(self, file_repository: FileRepositiory)-> None:
        self.file_repository = file_repository

    def execute(
        self,
        uploader_id: str,
        file_name: str,
        file_type,
        storage_path: str, 
        message_id: str = None,
        file_size: int = None,
        thumbnail_path: str = None
    )-> File:
        
        file = File(
            id=str(uuid.uuid4()),
            uploader_id=uploader_id,
            message_id=message_id,
            file_size=file_size,
            file_name=file_name,
            file_type=file_type,
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            created_at=datetime.utcnow()
        )


        self.file_repository.save(file)

        return file