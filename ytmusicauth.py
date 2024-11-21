from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import json

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']

class YouTubeMusic:
    def __init__(self, client_secrets_file, scopes, youtube_api_service_name, youtube_api_version):
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes
        self.youtube_api_service_name = youtube_api_service_name
        self.youtube_api_version = youtube_api_version
        self.youtube = self.get_authenticated_service()

    def get_authenticated_service(self):
        """
        Initialize YouTube API and returns object for API access
        """
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
        youtube = build(self.youtube_api_service_name, self.youtube_api_version, credentials=credentials)
        return youtube

    @staticmethod
    def update_progress(progress, playlist_title, i):
        progress[playlist_title]["last-track_index"] = i + 1
        with open("progress.json", "w") as f:
            json.dump(progress, f)