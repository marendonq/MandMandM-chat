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

# Prefijo distinto de /files (subida binaria en file.py) — solo metadatos en PostgreSQL
router = APIRouter(prefix="/file-metadata", tags=["file-metadata"])


def _to_response(entity) -> FileAssetResponse:
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
    items = [_to_response(x) for x in service.list_by_owner(owner_profile_id)]
    return FileAssetListResponse(items=items)


@router.get("/{asset_id}", response_model=FileAssetResponse)
@inject
def get_file_metadata(
    asset_id: str,
    service: FileAssetService = Depends(Provide[Container.file_asset_service]),
):
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
    try:
        service.delete(asset_id)
    except FileAssetNotFound:
        raise HTTPException(status_code=404, detail="File not found")
