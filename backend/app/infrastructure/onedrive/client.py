"""OneDrive client adapter — Microsoft Graph API integration."""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.models.onedrive_token import OneDriveToken
from backend.app.domain.ports.onedrive_client import IOneDriveClient

logger = logging.getLogger(__name__)

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# Default folder structure for equipment
EQUIPMENT_FOLDERS = [
    "01_ORDENES_DE_SERVICIO",
    "02_INFORMES",
    "03_FOTOS_EQUIPO",
    "04_MANUALES",
]

# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds


class OneDriveClient(IOneDriveClient):
    """Microsoft Graph API OneDrive adapter with token management and retry logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._client_id = os.getenv("AZURE_CLIENT_ID", "")
        self._client_secret = os.getenv("AZURE_CLIENT_SECRET", "")
        self._tenant_id = os.getenv("AZURE_TENANT_ID", "")

    @property
    def _token_url(self) -> str:
        return f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"

    async def _get_access_token(self) -> str:
        """Retrieve a valid access token, refreshing if necessary.

        Fetches the singleton token row from the database. If expired,
        uses the refresh token to obtain a new access token via the
        OAuth2 client_credentials or refresh_token flow.

        Returns:
            Valid access token string.

        Raises:
            RuntimeError: If no tokens are configured or refresh fails.
        """
        result = await self.session.execute(select(OneDriveToken).where(OneDriveToken.id == 1))
        token_row = result.scalar_one_or_none()

        if token_row is None or token_row.access_token is None:
            raise RuntimeError(
                "OneDrive tokens not configured. "
                "Complete the OAuth2 authorization flow first."
            )

        # Check if token is still valid (with 5-minute buffer)
        if token_row.expires_at and token_row.expires_at > datetime.now(timezone.utc) + timedelta(minutes=5):
            return token_row.access_token

        # Token expired — attempt refresh
        if token_row.refresh_token:
            new_token = await self._refresh_token(token_row.refresh_token)
            if new_token:
                return new_token

        # If refresh failed, return existing token and let caller handle 401
        logger.warning("OneDrive token refresh failed — returning stale token")
        return token_row.access_token

    async def _refresh_token(self, refresh_token: str) -> Optional[str]:
        """Exchange refresh token for a new access token.

        Args:
            refresh_token: The current refresh token.

        Returns:
            New access token if successful, None otherwise.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._token_url,
                    data={
                        "client_id": self._client_id,
                        "client_secret": self._client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token",
                        "scope": "Files.ReadWrite offline_access",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    new_access = data["access_token"]
                    new_refresh = data.get("refresh_token", refresh_token)
                    expires_in = data.get("expires_in", 3600)

                    # Persist updated tokens
                    result = await self.session.execute(
                        select(OneDriveToken).where(OneDriveToken.id == 1)
                    )
                    token_row = result.scalar_one_or_none()
                    if token_row:
                        token_row.access_token = new_access
                        token_row.refresh_token = new_refresh
                        token_row.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                        await self.session.flush()

                    logger.info("OneDrive token refreshed successfully")
                    return new_access
                else:
                    logger.error(
                        "OneDrive token refresh failed: %s %s",
                        response.status_code,
                        response.text,
                    )
                    return None
            except httpx.HTTPError as e:
                logger.error("OneDrive token refresh HTTP error: %s", e)
                return None

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> httpx.Response:
        """Execute an HTTP request with exponential backoff retry.

        Handles rate limiting (429) with Retry-After header support,
        and transient failures (5xx) with exponential backoff.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            url: Full URL to request.
            **kwargs: Additional arguments passed to httpx client.

        Returns:
            httpx.Response object.

        Raises:
            httpx.HTTPStatusError: On non-retryable errors after all attempts.
        """
        last_exception = None

        for attempt in range(MAX_RETRIES):
            try:
                token = await self._get_access_token()
                headers = kwargs.pop("headers", {})
                headers["Authorization"] = f"Bearer {token}"

                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method, url, headers=headers, **kwargs
                    )

                    # Rate limited — respect Retry-After
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", BASE_DELAY * (2 ** attempt)))
                        logger.warning("OneDrive rate limited — retrying after %ds", retry_after)
                        await asyncio.sleep(retry_after)
                        continue

                    # Server errors — retry with backoff
                    if response.status_code >= 500:
                        delay = BASE_DELAY * (2 ** attempt)
                        logger.warning(
                            "OneDrive server error %d — retrying in %ds (attempt %d/%d)",
                            response.status_code, delay, attempt + 1, MAX_RETRIES,
                        )
                        await asyncio.sleep(delay)
                        continue

                    response.raise_for_status()
                    return response

            except httpx.HTTPStatusError:
                raise
            except httpx.HTTPError as e:
                last_exception = e
                delay = BASE_DELAY * (2 ** attempt)
                logger.warning(
                    "OneDrive request failed: %s — retrying in %ds (attempt %d/%d)",
                    e, delay, attempt + 1, MAX_RETRIES,
                )
                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception
        raise RuntimeError("OneDrive request failed after all retries")

    async def create_folder(self, parent_path: str, folder_name: str) -> str:
        """Create a folder in OneDrive under the given parent path.

        Args:
            parent_path: The path of the parent folder (e.g., "/Equipment").
            folder_name: Name of the folder to create.

        Returns:
            The ID of the created (or existing) folder.
        """
        # Check if folder already exists
        existing = await self._find_item_by_path(parent_path)
        if existing:
            parent_id = existing["id"]
        else:
            # Create parent path first
            parent_id = await self._ensure_path(parent_path)

        # Check if child folder already exists
        url = f"{GRAPH_BASE_URL}/me/drive/items/{parent_id}/children"
        response = await self._request_with_retry("GET", url)
        for child in response.json().get("value", []):
            if child.get("name") == folder_name and child.get("folder"):
                logger.info("OneDrive folder already exists: %s/%s", parent_path, folder_name)
                return child["id"]

        # Create the folder
        url = f"{GRAPH_BASE_URL}/me/drive/items/{parent_id}/children"
        payload = {
            "name": folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "fail",
        }
        response = await self._request_with_retry("POST", url, json=payload)
        folder_id = response.json()["id"]
        logger.info("Created OneDrive folder: %s/%s (id=%s)", parent_path, folder_name, folder_id)
        return folder_id

    async def upload_file(self, folder_path: str, file_name: str, file_content: bytes) -> str:
        """Upload a file to the specified OneDrive folder.

        Uses simple upload for files under 4MB and uploadSession for larger files.

        Args:
            folder_path: Path to the target folder in OneDrive.
            file_name: Name of the file to upload.
            file_content: Raw file bytes.

        Returns:
            The ID of the uploaded file item.
        """
        folder_id = await self._find_item_by_path(folder_path)
        if not folder_id:
            folder_id = await self._ensure_path(folder_path)
        else:
            folder_id = folder_id["id"]

        # Simple upload for files < 4MB
        if len(file_content) < 4 * 1024 * 1024:
            url = f"{GRAPH_BASE_URL}/me/drive/items/{folder_id}:/{file_name}:/content"
            response = await self._request_with_retry(
                "PUT",
                url,
                content=file_content,
                headers={"Content-Type": "application/octet-stream"},
            )
            item_id = response.json()["id"]
            logger.info("Uploaded file to OneDrive: %s/%s (id=%s)", folder_path, file_name, item_id)
            return item_id

        # Upload session for larger files (resumable)
        url = f"{GRAPH_BASE_URL}/me/drive/items/{folder_id}:/{file_name}:/createUploadSession"
        payload = {
            "item": {
                "@microsoft.graph.conflictBehavior": "replace",
                "name": file_name,
            }
        }
        response = await self._request_with_retry("POST", url, json=payload)
        upload_url = response.json()["uploadUrl"]

        # Upload in chunks
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        total_size = len(file_content)

        for i in range(0, total_size, chunk_size):
            chunk = file_content[i : i + chunk_size]
            end = min(i + chunk_size - 1, total_size - 1)

            async with httpx.AsyncClient() as client:
                token = await self._get_access_token()
                resp = await client.put(
                    upload_url,
                    content=chunk,
                    headers={
                        "Content-Range": f"bytes {i}-{end}/{total_size}",
                        "Content-Length": str(len(chunk)),
                    },
                )
                if resp.status_code not in (200, 201):
                    raise RuntimeError(f"Upload chunk failed: {resp.status_code} {resp.text}")

        # Final response is in the last PUT — get item from session
        result = await self._request_with_retry("GET", upload_url)
        item_id = result.json()["id"]
        logger.info("Uploaded large file to OneDrive: %s/%s (id=%s)", folder_path, file_name, item_id)
        return item_id

    async def get_folder_contents(self, folder_path: str) -> List[dict]:
        """Get contents of a OneDrive folder.

        Args:
            folder_path: Path to the folder in OneDrive.

        Returns:
            List of item dicts (files and subfolders).
        """
        item = await self._find_item_by_path(folder_path)
        if not item:
            return []

        url = f"{GRAPH_BASE_URL}/me/drive/items/{item['id']}/children"
        response = await self._request_with_retry("GET", url)
        return response.json().get("value", [])

    async def delete_item(self, item_path: str) -> bool:
        """Delete an item (file or folder) from OneDrive.

        Args:
            item_path: Full path to the item to delete.

        Returns:
            True if deleted, False if not found.
        """
        item = await self._find_item_by_path(item_path)
        if not item:
            return False

        url = f"{GRAPH_BASE_URL}/me/drive/items/{item['id']}"
        await self._request_with_retry("DELETE", url)
        logger.info("Deleted OneDrive item: %s", item_path)
        return True

    async def get_item_download_url(self, item_path: str) -> Optional[str]:
        """Get a temporary download URL for a OneDrive item.

        Args:
            item_path: Full path to the item.

        Returns:
            Download URL string, or None if not found.
        """
        item = await self._find_item_by_path(item_path)
        if not item:
            return None

        url = f"{GRAPH_BASE_URL}/me/drive/items/{item['id']}"
        response = await self._request_with_retry("GET", url)
        return response.json().get("@microsoft.graph.downloadUrl")

    async def check_connection(self) -> dict:
        """Check OneDrive connection status.

        Returns:
            Dict with connected status and user info.
        """
        try:
            url = f"{GRAPH_BASE_URL}/me"
            response = await self._request_with_retry("GET", url)
            user_data = response.json()
            return {
                "connected": True,
                "user": user_data.get("displayName", "Unknown"),
                "email": user_data.get("userPrincipalName", ""),
            }
        except Exception as e:
            logger.error("OneDrive connection check failed: %s", e)
            return {"connected": False, "error": str(e)}

    # --- Private helpers ---

    async def _find_item_by_path(self, path: str) -> Optional[dict]:
        """Find a drive item by its path.

        Args:
            path: Path relative to the drive root (e.g., "/Equipment/ABC").

        Returns:
            Item dict if found, None otherwise.
        """
        clean_path = path.strip("/")
        if not clean_path:
            return {"id": "root"}

        url = f"{GRAPH_BASE_URL}/me/drive/root:/{clean_path}"
        try:
            response = await self._request_with_retry("GET", url)
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def _ensure_path(self, path: str) -> str:
        """Ensure a nested path exists, creating folders as needed.

        Args:
            path: Path to ensure (e.g., "/Equipment/ABC/01_ORDENES").

        Returns:
            ID of the deepest folder in the path.
        """
        parts = [p for p in path.strip("/").split("/") if p]
        current_parent = "root"
        current_path = ""

        for part in parts:
            current_path = f"{current_path}/{part}"
            item = await self._find_item_by_path(current_path)
            if item:
                current_parent = item["id"]
            else:
                # Create this folder level
                url = f"{GRAPH_BASE_URL}/me/drive/items/{current_parent}/children"
                payload = {
                    "name": part,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "fail",
                }
                try:
                    response = await self._request_with_retry("POST", url, json=payload)
                    current_parent = response.json()["id"]
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 409:
                        # Folder already exists (conflict) — find it
                        item = await self._find_item_by_path(current_path)
                        if item:
                            current_parent = item["id"]
                        else:
                            raise
                    else:
                        raise

        return current_parent

    async def create_equipment_folders(self, equipment_path: str) -> dict:
        """Create the standard folder structure for equipment.

        Args:
            equipment_path: Base path for the equipment (e.g., "/Equipment/ABC123").

        Returns:
            Dict mapping folder names to their IDs.
        """
        folder_ids = {}
        for folder_name in EQUIPMENT_FOLDERS:
            folder_id = await self.create_folder(equipment_path, folder_name)
            folder_ids[folder_name] = folder_id
        return folder_ids
