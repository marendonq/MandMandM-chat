"""File management HTTP handlers for uploading, retrieving, and deleting files.

Exposes REST endpoints for file operations including binary upload,
metadata retrieval, file download, and deletion.
"""

import mimetypes
from pathlib import Path

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse as BinaryFileResponse
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
    """Convert a FileEntity to a FileResponse schema.

    Args:
        entity: The FileEntity domain object to convert.

    Returns:
        A FileResponse with the file metadata.
    """
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
    """Upload a new file to the system.

    Reads the uploaded file content, stores it in the storage backend,
    and persists the file metadata.

    Args:
        file: The file to upload (multipart form data).
        file_type: The type of file (image, document, video).
        uploader_id: ID of the user uploading the file.
        message_id: ID of the message this file is associated with.
        upload_service: Injected upload file service.

    Returns:
        FileResponse with the uploaded file metadata.

    Raises:
        HTTPException 400: If the file is empty or validation fails.
        HTTPException 500: If an internal error occurs during upload.
    """
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
    """Get file metadata by its ID.

    Args:
        file_id: The unique file identifier.
        service: Injected get file service.

    Returns:
        FileResponse with the file metadata.

    Raises:
        HTTPException 404: If the file is not found.
    """
    try:
        entity = service.execute(file_id)
        return _to_response(entity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{file_id}/download")
@inject
def download_file(
    file_id: str,
    service: GetFileService = Depends(Provide[Container.get_file_service]),
):
    """Download the binary content of a file.

    Retrieves the file from the storage backend and streams it
    to the client with the appropriate MIME type.

    Args:
        file_id: The unique file identifier.
        service: Injected get file service.

    Returns:
        Binary file response with the file content.

    Raises:
        HTTPException 404: If the file or stored file is not found.
    """
    try:
        entity = service.execute(file_id)
        file_path = Path(entity.storage_path)
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="Stored file not found")

        media_type, _ = mimetypes.guess_type(entity.file_name)
        return BinaryFileResponse(
            path=str(file_path),
            media_type=media_type or "application/octet-stream",
            filename=entity.file_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/message/{message_id}", response_model=list[FileResponse])
@inject
def get_files_by_message(
    message_id: str,
    service: GetFilesByMessageService = Depends(Provide[Container.get_files_by_message_service]),
):
    """Get all files associated with a specific message.

    Args:
        message_id: The ID of the message to get files for.
        service: Injected get files by message service.

    Returns:
        A list of FileResponse objects for the message.
    """
    entities = service.execute(message_id)
    return [_to_response(entity) for entity in entities]


@router.delete("/{file_id}")
@inject
def delete_file(
    file_id: str,
    service: DeleteFileService = Depends(Provide[Container.delete_file_service]),
):
    """Delete a file from storage and its metadata.

    Args:
        file_id: The unique file identifier to delete.
        service: Injected delete file service.

    Returns:
        A success message.

    Raises:
        HTTPException 404: If the file is not found.
    """
    try:
        service.execute(file_id)
        return {"message": "File deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

