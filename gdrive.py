# gdrive.py
from io import BytesIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

MIMETYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

class DriveClient:
    def __init__(self, credentials):
        self.svc = build("drive", "v3", credentials=credentials)

    def download_bytes(self, file_id: str) -> bytes:
        req = self.svc.files().get_media(fileId=file_id)
        buf = BytesIO()
        dl = MediaIoBaseDownload(buf, req)
        done = False
        while not done:
            status, done = dl.next_chunk()
        buf.seek(0)
        return buf.read()

    def update_bytes(self, file_id: str, content: bytes, mime=MIMETYPE_XLSX):
        media = MediaIoBaseUpload(BytesIO(content), mimetype=mime, resumable=True)
        return self.svc.files().update(fileId=file_id, media_body=media).execute()
