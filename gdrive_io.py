from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from typing import List, Dict, Optional

MIMETYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

class DriveClient:
    def __init__(self, credentials):
        # credentials is a google.oauth2.credentials.Credentials from google_auth.get_creds()
        self.service = build("drive", "v3", credentials=credentials)

    def download_file(self, file_id: str) -> bytes:
        """Return file content as bytes for the given Drive fileId."""
        request = self.service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return fh.read()

    def update_file_content(self, file_id: str, content_bytes: bytes, mime_type: str):
        """Overwrite file content (resumable upload)."""
        media = MediaIoBaseUpload(BytesIO(content_bytes), mimetype=mime_type, resumable=True)
        return self.service.files().update(fileId=file_id, media_body=media).execute()

    def list_files(self, q: Optional[str] = None, page_size: int = 100, page_token: Optional[str] = None) -> Dict:
        """
        List files in the user's Drive with optional pagination.

        Args:
            q: An optional Drive API query string (https://developers.google.com/drive/api/v3/search-files).
               Example to list spreadsheets: "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
            page_size: max results to return per page (Drive supports up to 1000; default to 100)
            page_token: optional token for pagination

        Returns:
            A dict with keys:
              - files: list of file dicts with at least 'id', 'name', 'mimeType', 'owners'
              - nextPageToken: token string or None
        """
        resp = self.service.files().list(
            q=q,
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType, owners(displayName))",
            pageToken=page_token
        ).execute()
        return {
            "files": resp.get("files", []),
            "nextPageToken": resp.get("nextPageToken")
        }