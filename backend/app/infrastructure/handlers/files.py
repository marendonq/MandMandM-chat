"""File asset metadata HTTP handlers for PostgreSQL-stored file records.

Exposes REST endpoints for registering, retrieving, and deleting
file asset metadata. Uses a different prefix (/file-metadata) from
the binary file upload handler (/files).
"""

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException

from app.application.services.file_asset import FileAssetService
from app.domain.exceptions import FileAssetNotFound
from app.infrastructure.container import Container
from app.infrastructure.schemas.file_asset import (
    FileAssetListResponse,
    FileAssetRegisterRequest,
    FileAssetResponse,
)

# Different prefix from /files (binary upload in file.py) — metadata only in PostgreSQL
router = APIRouter(prefix="/file-metadata", tags=["file-metadata"])


def _to_response(entity) -> FileAssetResponse:
    """Convert a FileAssetEntity to a FileAssetResponse schema.

    Args:
        entity: The FileAssetEntity domain object to convert.

    Returns:
        A FileAssetResponse with the file asset metadata.
    """
    return FileAssetResponse(
        id=entity.id,
        owner_profile_id=entity.owner_profile_id,
        original_name=entity.original_name,
        mime_type=entity.mime_type,
        size_bytes=entity.size_bytes,
        storage_key=entity.storage_key,
        created_at=entity.created_at,
    )


@router.post("/", response_model=FileAssetResponse)
@inject
def register_file_metadata(
    body: FileAssetRegisterRequest,
    service: FileAssetService = Depends(Provide[Container.file_asset_service]),
):
    """Register metadata for a new file asset.

    Creates a file asset record in PostgreSQL with the provided metadata.

    Args:
        body: The file asset registration request data.
        service: Injected file asset service.

    Returns:
        FileAssetResponse with the registered file asset metadata.
    """
    entity = service.register_metadata(
        owner_profile_id=body.owner_profile_id,
        original_name=body.original_name,
        mime_type=body.mime_type,
        size_bytes=body.size_bytes,
        storage_key=body.storage_key,
    )
    return _to_response(entity)


@router.get("/by-owner/{owner_profile_id}", response_model=FileAssetListResponse)
@inject
def list_files_by_owner(
    owner_profile_id: str,
    service: FileAssetService = Depends(Provide[Container.file_asset_service]),
):
    """List all file assets owned by a specific user profile.

    Args:
        owner_profile_id: The ID of the user profile to query.
        service: Injected file asset service.

    Returns:
        FileAssetListResponse with all file assets for the user.
    """
    items = [_to_response(x) for x in service.list_by_owner(owner_profile_id)]
    return FileAssetListResponse(items=items)


@router.get("/{asset_id}", response_model=FileAssetResponse)
@inject
def get_file_metadata(
    asset_id: str,
    service: FileAssetService = Depends(Provide[Container.file_asset_service]),
):
    """Get file asset metadata by its ID.

    Args:
        asset_id: The unique file asset identifier.
        service: Injected file asset service.

    Returns:
        FileAssetResponse with the file asset metadata.

    Raises:
        HTTPException 404: If the file asset is not found.
    """
    try:
        return _to_response(service.get(asset_id))
    except FileAssetNotFound:
        raise HTTPException(status_code=404, detail="File not found")


@router.delete("/{asset_id}", status_code=204)
@inject
def delete_file_metadata(
    asset_id: str,
    service: FileAssetService = Depends(Provide[Container.file_asset_service]),
):
    """Delete file asset metadata by its ID.

    Args:
        asset_id: The unique file asset identifier to delete.
        service: Injected file asset service.

    Raises:
        HTTPException 404: If the file asset is not found.
    """
    try:
        service.delete(asset_id)
    except FileAssetNotFound:
        raise HTTPException(status_code=404, detail="File not found")
