from datetime import datetime, timedelta
from src.homelab_services.journiv.schemas import EntryCreate, EntryResponse, EntryTagResponse, Mood, MoodLogCreate, MoodLogResponse, MoodLogUpdate, Tag
from src.config import Config
import requests
from typing import List, Optional
from src.logger import logger
from random import choice

    
class JournivClient:
    def __init__(self):
        self.base_url = Config.JOURNIV_BASE_URL
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self) -> bool:
        """Login and store tokens"""
        url = f"{self.base_url}/api/v1/auth/login"

        payload = {"email": Config.JOURNIV_EMAIL, "password": Config.JOURNIV_PASSWORD}
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            logger.info("Logged in to Journiv")
            return True
        logger.error("Failed to log in to Journiv")
        return False

    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return False
            
        url = f"{self.base_url}/api/v1/auth/refresh"
        payload = {"refresh_token": self.refresh_token}
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            return True
        return False

    def _get_headers(self) -> dict:
        """Get headers with auth token"""
        if not self.access_token:
            raise ValueError("Not authenticated. Call login() first.")
        return {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

    def get_journal_entries(self, journal_id: str, limit: int = 50, offset: int = 0, include_pinned: bool = True) -> List[EntryResponse]:
        """Get entries for a specific journal"""
        url = f"{self.base_url}/api/v1/entries/journal/{journal_id}"
        
        params = {
            'limit': min(limit, 100),  # API limits to 100 max
            'offset': offset,
            'include_pinned': str(include_pinned).lower()
        }
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code == 200:
            entries_data = response.json()
            return [EntryResponse(**entry) for entry in entries_data]
        elif response.status_code == 401:
            if self.refresh_access_token():
                response = requests.get(url, headers=self._get_headers(), params=params)
                if response.status_code == 200:
                    entries_data = response.json()
                    return [EntryResponse(**entry) for entry in entries_data]
        
        response.raise_for_status()
        return []

    def get_all_journal_entries(self, journal_id: str) -> List[EntryResponse]:
        """Get all entries for a journal (handles pagination)"""
        all_entries = []
        limit = 100  # Max per request
        offset = 0
        
        while True:
            entries = self.get_journal_entries(journal_id, limit=limit, offset=offset)
            if not entries:
                break
                
            all_entries.extend(entries)
            
            # If we got fewer than the limit, we've reached the end
            if len(entries) < limit:
                break
                
            offset += limit
        
        return all_entries

    def get_entries_by_date(self, entries: List[EntryResponse], target_date: str) -> List[EntryResponse]:
        """Get all entries for a specific date (YYYY-MM-DD format) from a given list"""
        # Filter entries by date
        matching_entries = []
        for entry in entries:
            if entry.entry_date == target_date:
                matching_entries.append(entry)
        
        return matching_entries
    
    def get_entries_by_date_range(
        self, 
        start_date: str, 
        end_date: str, 
        journal_id: Optional[str] = None
    ) -> List[EntryResponse]:
        """
        Get entries within a date range based on entry_date field.
        Optionally filter by journal_id.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            journal_id: Optional journal ID to filter by
            
        Returns:
            List of EntryResponse objects
            
        Raises:
            requests.HTTPError: If the API request fails
            ValueError: If date format is invalid
        """
        # Validate date format
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {e}")
        
        url = f"{self.base_url}/api/v1/entries/date-range"
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        if journal_id:
            params['journal_id'] = journal_id
        
        response = requests.get(
            url, 
            headers=self._get_headers(),
            params=params,
        )
        
        if response.status_code == 200:
            entries_data = response.json()
            return [EntryResponse(**entry) for entry in entries_data]
        elif response.status_code == 401:
            # Token might be expired, try to refresh
            if self.refresh_access_token():
                # Retry with new token
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    cookies=self._get_cookies()
                )
                if response.status_code == 200:
                    entries_data = response.json()
                    return [EntryResponse(**entry) for entry in entries_data]
        
        # If we get here, the request failed
        response.raise_for_status()
        return []

    ###########################################################################
    # Moods
    ###########################################################################
    
    def get_mood_logs(self, entry_id: Optional[str] = None, mood_id: Optional[str] = None, 
                     start_date: Optional[str] = None, end_date: Optional[str] = None,
                     limit: int = 50, offset: int = 0) -> List[MoodLogResponse]:
        """Get mood logs for the current user with optional filters"""
        url = f"{self.base_url}/api/v1/moods/logs"
        
        params = {
            'limit': min(limit, 100),
            'offset': offset
        }
        
        if entry_id:
            params['entry_id'] = entry_id
        if mood_id:
            params['mood_id'] = mood_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code == 200:
            logs_data = response.json()
            return [MoodLogResponse(**log) for log in logs_data]
        elif response.status_code == 401:
            if self.refresh_access_token():
                response = requests.get(url, headers=self._get_headers(), params=params)
                if response.status_code == 200:
                    logs_data = response.json()
                    return [MoodLogResponse(**log) for log in logs_data]
        
        response.raise_for_status()
        return []

    def entry_has_mood_log(self, entry_id: str) -> bool:
        """Check if an entry already has a mood logged to it"""
        mood_logs = self.get_mood_logs(entry_id=entry_id, limit=1)
        return len(mood_logs) > 0


    
    ###########################################################################
    # People
    ###########################################################################
    def add_tag_to_entry(self, entry_id: str, tag_id: str) -> EntryTagResponse:
        """Add a tag to an entry"""
        url = f"{self.base_url}/api/v1/tags/entry/{entry_id}/tag/{tag_id}"
        
        response = requests.post(url, headers=self._get_headers())
        
        if response.status_code == 201:
            return EntryTagResponse(**response.json())
        elif response.status_code == 401:
            if self.refresh_access_token():
                response = requests.post(url, headers=self._get_headers())
                if response.status_code == 201:
                    return EntryTagResponse(**response.json())
        
        response.raise_for_status()

    def get_tags(self, limit: int = 50, offset: int = 0, search: Optional[str] = None) -> List[Tag]:
        """Get tags for the current user"""
        url = f"{self.base_url}/api/v1/tags/"
        
        params = {
            'limit': min(limit, 100),
            'offset': offset
        }
        if search:
            params['search'] = search
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code == 200:
            tags_data = response.json()
            return [Tag(**tag) for tag in tags_data]
        elif response.status_code == 401:
            if self.refresh_access_token():
                response = requests.get(url, headers=self._get_headers(), params=params)
                if response.status_code == 200:
                    tags_data = response.json()
                    return [Tag(**tag) for tag in tags_data]
        
        response.raise_for_status()
        return []

    def get_all_tags(self, search: Optional[str] = None) -> List[Tag]:
        """Get all tags for the current user (handles pagination)"""
        all_tags = []
        limit = 100  # Max per request
        offset = 0
        
        while True:
            tags = self.get_tags(limit=limit, offset=offset, search=search)
            if not tags:
                break
                
            all_tags.extend(tags)
            
            # If we got fewer than the limit, we've reached the end
            if len(tags) < limit:
                break
                
            offset += limit
        
        return all_tags

    def get_tag_by_name(self, tag_name: str) -> Optional[Tag]:
        """Get a tag by name (case-insensitive)"""
        all_tags = self.get_all_tags()
        tag_name_lower = tag_name.lower()
        
        for tag in all_tags:
            if tag.name.lower() == tag_name_lower:
                return tag
        return None

    def get_entry_tags(self, entry_id: str) -> List[Tag]:
        """Get all tags for an entry"""
        url = f"{self.base_url}/api/v1/tags/entry/{entry_id}"
        
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            tags_data = response.json()
            return [Tag(**tag) for tag in tags_data]
        elif response.status_code == 401:
            if self.refresh_access_token():
                response = requests.get(url, headers=self._get_headers())
                if response.status_code == 200:
                    tags_data = response.json()
                    return [Tag(**tag) for tag in tags_data]
        
        response.raise_for_status()
        return []

if __name__ == "__main__":
    client = JournivClient()
    client.login()
    # Get all moods
    entries = client.get_mood_logs(entry_id="1926b9fd-57b6-41a8-81b0-0e90c1de6bd5")
    pass