"""OneDrive client port."""

from abc import ABC, abstractmethod
from typing import List, Optional


class IOneDriveClient(ABC):
    """Abstract OneDrive client interface."""

    @abstractmethod
    async def create_folder(self, parent_path: str, folder_name: str) -> str:
        """Create a folder in OneDrive and return its ID."""
        ...

    @abstractmethod
    async def upload_file(self, folder_path: str, file_name: str, file_content: bytes) -> str:
        """Upload a file to OneDrive and return its ID."""
        ...

    @abstractmethod
    async def get_folder_contents(self, folder_path: str) -> List[dict]:
        """Get contents of a folder."""
        ...
