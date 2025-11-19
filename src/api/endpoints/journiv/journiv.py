from fastapi import APIRouter, HTTPException, Depends
from typing import List

from pydantic import BaseModel

from homelab_services.journiv.schemas import EntryResponse
from src.homelab_services.journiv.journiv import JournivClient
from src.config import Config

router = APIRouter()

class JournalEntryResponse(BaseModel):
    id: str
    title: str
    content: str
    entry_date: str
    created_at: str
    updated_at: str

def get_journiv_client():
    """Dependency to get Journiv client instance"""
    client = JournivClient()
    if not client.login():
        raise HTTPException(status_code=401, detail="Failed to authenticate with Journiv")
    return client

@router.get("/journal-entries", response_model=List[JournalEntryResponse])
async def get_all_journal_entries(
    client: JournivClient = Depends(get_journiv_client)
):
    """
    Get all journal entries from Journiv and return them in TypeScript interface format
    """
    try:
        # Get all entries from Journiv
        entries: List[EntryResponse] = client.get_all_journal_entries(Config.JOURNIV_JOURNAL_ID)
        
        # Convert to the response model that matches TypeScript interface
        response_entries = []
        for entry in entries:
            response_entries.append(JournalEntryResponse(
                id=entry.id,
                title=entry.title,
                content=entry.content,
                entry_date=entry.entry_date,
                created_at=entry.entry_date,
                updated_at=entry.entry_date
            ))
        
        return response_entries
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching journal entries: {str(e)}")

@router.get("/journal-entries/paginated", response_model=dict)
async def get_paginated_journal_entries(
    journal_id: str,
    page: int = 1,
    limit: int = 10,
    client: JournivClient = Depends(get_journiv_client)
):
    """
    Get paginated journal entries from Journiv
    """
    try:
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get paginated entries
        entries = client.get_journal_entries(journal_id, limit=limit, offset=offset)
        
        # Get total count for pagination info
        all_entries = client.get_all_journal_entries(journal_id)
        total_count = len(all_entries)
        
        # Convert to response model
        response_entries = []
        for entry in entries:
            response_entries.append(JournalEntryResponse(
                id=entry.id,
                title=entry.title,
                content=entry.content,
                entry_date=entry.entry_date,
                created_at=entry.created_at,
                updated_at=entry.updated_at
            ))
        
        return {
            "entries": response_entries,
            "pagination": {
                "currentPage": page,
                "totalPages": (total_count + limit - 1) // limit,  # Ceiling division
                "totalCount": total_count,
                "hasNext": page < ((total_count + limit - 1) // limit),
                "hasPrevious": page > 1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching journal entries: {str(e)}")