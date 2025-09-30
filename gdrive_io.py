# gdrive_io.py
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

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
