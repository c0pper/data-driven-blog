from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Enums from Immich documentation
class AssetOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class AssetTypeEnum(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    OTHER = "OTHER"

class AssetVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


# Request models
class SearchAssetsRequest(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    albumIds: Optional[List[UUID]] = None
    checksum: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    createdAfter: Optional[datetime] = None
    createdBefore: Optional[datetime] = None
    description: Optional[str] = None
    deviceAssetId: Optional[str] = None
    deviceId: Optional[str] = None
    encodedVideoPath: Optional[str] = None
    id: Optional[UUID] = None
    isEncoded: Optional[bool] = None
    isFavorite: Optional[bool] = None
    isMotion: Optional[bool] = None
    isNotInAlbum: Optional[bool] = None
    isOffline: Optional[bool] = None
    lensModel: Optional[str] = None
    libraryId: Optional[UUID] = None
    make: Optional[str] = None
    model: Optional[str] = None
    ocr: Optional[str] = None
    order: Optional[AssetOrder] = None
    originalFileName: Optional[str] = None
    originalPath: Optional[str] = None
    page: Optional[int] = Field(default=1, ge=1)
    personIds: Optional[List[UUID]] = None
    previewPath: Optional[str] = None
    rating: Optional[int] = Field(None, ge=0, le=5)
    size: Optional[int] = None
    state: Optional[str] = None
    tagIds: Optional[List[UUID]] = None
    takenAfter: Optional[datetime] = None
    takenBefore: Optional[datetime] = None
    thumbnailPath: Optional[str] = None
    trashedAfter: Optional[datetime] = None
    trashedBefore: Optional[datetime] = None
    type: Optional[AssetTypeEnum] = None
    updatedAfter: Optional[datetime] = None
    updatedBefore: Optional[datetime] = None
    visibility: Optional[AssetVisibility] = None
    withDeleted: Optional[bool] = None
    withExif: Optional[bool] = None
    withPeople: Optional[bool] = None
    withStacked: Optional[bool] = None


# Response models
class SearchAlbumResponseDto(BaseModel):
    id: UUID
    albumName: str
    description: Optional[str] = None
    albumThumbnailAssetId: Optional[UUID] = None
    createdAt: datetime
    updatedAt: datetime
    albumUsers: List[dict]  # Could be refined with a proper model
    assets: List[dict]  # Could be refined with a proper model
    ownerId: UUID
    shared: bool
    assetCount: int


class ExifResponseDto(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    exifImageWidth: Optional[int] = None
    exifImageHeight: Optional[int] = None
    fileSizeInByte: Optional[int] = None
    orientation: Optional[str] = None
    dateTimeOriginal: Optional[datetime] = None
    modifyDate: Optional[datetime] = None
    timeZone: Optional[str] = None
    lensModel: Optional[str] = None
    fNumber: Optional[float] = None
    focalLength: Optional[float] = None
    iso: Optional[int] = None
    exposureTime: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None


class SearchAssetResponseDto(BaseModel):
    id: UUID
    deviceAssetId: str
    ownerId: UUID
    deviceId: str
    type: AssetTypeEnum
    originalPath: str
    originalFileName: str
    resized: bool
    thumbhash: Optional[str] = None
    fileCreatedAt: datetime
    fileModifiedAt: datetime
    updatedAt: datetime
    isFavorite: bool
    isArchived: bool
    duration: Optional[str] = None
    exifInfo: Optional[ExifResponseDto] = None
    livePhotoVideoId: Optional[UUID] = None
    tags: List[dict] = []  # Could be refined with a proper model
    people: List[dict] = []  # Could be refined with a proper model
    checksum: str


class SearchMetadataResponse(BaseModel):
    albums: SearchAlbumResponseDto
    assets: SearchAssetResponseDto
