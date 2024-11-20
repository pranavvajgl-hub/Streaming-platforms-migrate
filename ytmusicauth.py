import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_KEY = os.getenv('API_KEY')

def get_authenticated_service(client_secrets_file, scopes, youtube_api_service_name, youtube_api_version):
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)
    return youtube

