import googleapiclient.discovery
import google_auth_oauthlib.flow

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
CLIENT_SECRETS_FILE = 'credentials.json'

def get_authenticated_service():
    """
    Funkce pro přihlášení k YouTube Music API pomocí OAuth2.
    """

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(host='localhost',

                                       port=8080,
                                       authorization_prompt_message='Please visit this URL: {url}',
                                       success_message='The auth flow is complete; you may close this window.',
                                       open_browser=True)

    return googleapiclient.discovery.build(API_SERVICE_NAME,
                                          API_VERSION,
                                          credentials=credentials)