from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.application.services.file import (
    UploadFileService,
    GetFileService,
    GetFilesByMessageService,
    DeleteFileService
)
from app.infrastructure.container import Container
from app.infrastructure.schemas.file import FileResponse

router = APIRouter(prefix="/files", tags=["files"])


def _to_response(entity) -> FileResponse:
    return FileResponse(
        id=entity.id,
        file_name=entity.file_name,
        file_type=entity.file_type.value if hasattr(entity.file_type, 'value') else entity.file_type,
        uploader_id=entity.uploader_id,
        storage_path=entity.storage_path,
        created_at=entity.created_at,
        file_size=entity.file_size,
        message_id=entity.message_id,
        thumbnail_path=entity.thumbnail_path,
    )


@router.post("/upload", response_model=FileResponse)
@inject
def upload_file(
    file: UploadFile = File(...),
    file_type: str = "document",
    uploader_id: str = "",
    message_id: str = "",
    upload_service: UploadFileService = Depends(Provide[Container.upload_file_service]),
):
    try:
        # Read file content
        file_bytes = file.file.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="File is empty")

        # Get file type enum
        from app.domain.entities.file import FileType
        file_type_enum = FileType(file_type)

        # Upload file
        entity = upload_service.execute(
            file_bytes=file_bytes,
            file_name=file.filename,
            file_type=file_type_enum,
            uploader_id=uploader_id,
            message_id=message_id,
        )

        return _to_response(entity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/{file_id}", response_model=FileResponse)
@inject
def get_file(
    file_id: str,
    service: GetFileService = Depends(Provide[Container.get_file_service]),
):
    try:
        entity = service.execute(file_id)
        return _to_response(entity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/message/{message_id}", response_model=list[FileResponse])
@inject
def get_files_by_message(
    message_id: str,
    service: GetFilesByMessageService = Depends(Provide[Container.get_files_by_message_service]),
):
    entities = service.execute(message_id)
    return [_to_response(entity) for entity in entities]


@router.delete("/{file_id}")
@inject
def delete_file(
    file_id: str,
    service: DeleteFileService = Depends(Provide[Container.delete_file_service]),
):
    try:
        service.execute(file_id)
        return {"message": "File deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

