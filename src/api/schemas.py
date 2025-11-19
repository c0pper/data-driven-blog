from pydantic import BaseModel
from typing import Optional
from src.api.endpoints.immich.schemas import SearchAssetResponseDto

class BlogPost(BaseModel):
    id: str
    title: str
    content: str
    created_at: str
    media: Optional[SearchAssetResponseDto] = None
