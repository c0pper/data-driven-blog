from src.api.endpoints.immich.schemas import SearchAssetsRequest, SearchMetadataResponse, AssetOrder
from typing import List, Optional
from datetime import datetime
from src.config import Config

# FastAPI endpoint
from fastapi import APIRouter, HTTPException, Depends
import httpx

router = APIRouter(prefix="/immich", tags=["immich"])


# Configuration for your Immich instance
class ImmichConfig:
    def __init__(self):
        self.base_url = Config.IMMICH_BASE_URL  # Update with your server
        self.api_key = Config.IMMICH_API_KEY  # Set your API key

config = ImmichConfig()


async def get_immich_headers():
    """Get headers for Immich API requests"""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": config.api_key
    }


@router.post("/search/assets", response_model=SearchMetadataResponse)
async def search_assets(
    search_request: SearchAssetsRequest,
    headers: dict = Depends(get_immich_headers)
):
    """
    Search for assets in Immich based on various criteria.
    Requires 'asset.read' permission.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/api/search/metadata",
                json=search_request.model_dump(exclude_unset=True),
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Immich API error: {response.text}"
                )
            
            return response.json()
            
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to Immich server: {str(e)}"
        )


# Specialized endpoint for getting assets on a particular date
@router.post("/search/assets/date/{target_date}")
async def search_assets_by_date(
    target_date: str,  # Format: YYYY-MM-DD
    with_exif: bool = True,
    headers: dict = Depends(get_immich_headers)
):
    """
    Search for assets taken on a specific date.
    """
    try:
        # Parse the target date and create date range
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        taken_after = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        taken_before = target_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        search_request = SearchAssetsRequest(
            takenAfter=taken_after,
            takenBefore=taken_before,
            withExif=with_exif,
            order=AssetOrder.ASC
        )
        
        # Convert to JSON-serializable dict
        request_data = search_request.model_dump(exclude_none=True, mode='json')
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{config.base_url}/api/search/metadata",
                json=request_data,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Immich API error: {response.text}"
                )
            
            return response.json()
            
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to Immich server: {str(e)}"
        )


# Utility function to get assets for analysis
def get_assets_for_analysis(assets_response: SearchMetadataResponse) -> List[dict]:
    """
    Extract assets data suitable for data analysis.
    Returns a list of dictionaries with key asset properties.
    """
    analysis_data = []
    
    # This would need to be adapted based on the actual response structure
    # from Immich, as the documentation shows 'assets' and 'albums' as separate
    # top-level fields in the response
    
    if hasattr(assets_response, 'assets'):
        for asset in assets_response.assets:
            asset_data = {
                'id': str(asset.id),
                'type': asset.type,
                'fileCreatedAt': asset.fileCreatedAt,
                'isFavorite': asset.isFavorite,
                'isArchived': asset.isArchived,
                'originalFileName': asset.originalFileName,
                'checksum': asset.checksum
            }
            
            # Add EXIF data if available
            if asset.exifInfo:
                asset_data.update({
                    'make': asset.exifInfo.make,
                    'model': asset.exifInfo.model,
                    'width': asset.exifInfo.exifImageWidth,
                    'height': asset.exifInfo.exifImageHeight,
                    'fileSize': asset.exifInfo.fileSizeInByte,
                    'latitude': asset.exifInfo.latitude,
                    'longitude': asset.exifInfo.longitude,
                    'city': asset.exifInfo.city,
                    'country': asset.exifInfo.country
                })
            
            analysis_data.append(asset_data)
    
    return analysis_data


if __name__ == "__main__":
    import asyncio
    # Example usage
    ass = asyncio.run(search_assets_by_date("2022-01-01"))
    pass