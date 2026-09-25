import os
from io import BytesIO

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def _credentials():
    token_path = os.getenv('GOOGLE_DRIVE_TOKEN', 'token.json')
    credentials_path = os.getenv('GOOGLE_DRIVE_CREDENTIALS', 'credentials.json')
    credentials = Credentials.from_authorized_user_file(token_path, SCOPES) if os.path.exists(token_path) else None

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        with open(token_path, 'w', encoding='utf-8') as token_file:
            token_file.write(credentials.to_json())
    elif not credentials or not credentials.valid:
        if not os.path.exists(credentials_path):
            raise RuntimeError(
                'Google Drive is not configured. Download OAuth credentials.json '
                'from Google Cloud and place it in the project folder.'
            )
        credentials = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES).run_local_server(port=0)
        with open(token_path, 'w', encoding='utf-8') as token_file:
            token_file.write(credentials.to_json())

    return credentials


def _service():
    return build('drive', 'v3', credentials=_credentials(), cache_discovery=False)


def upload_encrypted(data, filename):
    metadata = {'name': filename}
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    if folder_id:
        metadata['parents'] = [folder_id]

    media = MediaIoBaseUpload(BytesIO(data), mimetype='application/octet-stream', resumable=True)
    result = _service().files().create(body=metadata, media_body=media, fields='id').execute()
    return result['id']


def download_encrypted(file_id):
    request = _service().files().get_media(fileId=file_id)
    output = BytesIO()
    downloader = MediaIoBaseDownload(output, request)
    complete = False
    while not complete:
        _, complete = downloader.next_chunk()
    return output.getvalue()