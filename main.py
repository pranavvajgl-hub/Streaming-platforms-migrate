import json
import os
from urllib.error import HTTPError
import time
import spotipy
from dotenv import load_dotenv
from spotauth import Spotify
from ytmusicauth import YouTubeMusic

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = os.getenv('SCOPE')

# Config for YouTube API
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/youtube']
API_KEY = os.getenv('API_KEY')

# Initiaize Spotify API
spotify = Spotify(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, SCOPE)
sp = spotify.sp

# Initiaize YouTube API
youtube_music = YouTubeMusic(CLIENT_SECRETS_FILE, SCOPES, YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION)
youtube = youtube_music.youtube

# Načtení stavu
if os.path.exists("progress.json"):
    with open("progress.json", "r") as f:
        progress = json.load(f)
else:
    progress = {}

try:
    playlists = sp.current_user_playlists()
except spotipy.SpotifyException as e:
    print(f"Chyba Spotify API: {e}")
    exit()

# Pro každý playlist:
for playlist in playlists['items']:
    try:
        playlist_title = playlist['name']

        # Kontrola existence alba
        if playlist_title in progress:
            playlist_id = progress[playlist_title]["id"]
            last_track_index = progress[playlist_title]["last_track_index"]
            print(f"Album '{playlist_title}' již existuje. Pokračování od indexu {last_track_index}.")
        else:
            # Vytvoření nového alba
            time.sleep(1)
            playlist_response = youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": playlist_title,
                        "description": f"Playlist převedený ze Spotify",
                    },
                    "status": {
                        "privacyStatus": "private"
                    }
                }
            ).execute()

            playlist_id = playlist_response['id']
            print(f"Vytvořen playlist na YouTube: {playlist_title} ({playlist_id})")
            last_track_index = 0
            progress[playlist_title] = {"id": playlist_id, "last_track_index": last_track_index}

        tracks = sp.playlist_tracks(playlist['id'])
        for i, track in enumerate(tracks['items']):
            if i < last_track_index:
                continue  # Přeskočení již přidaných skladeb

            try:
                # Získání informací o skladbě
                track_name = track['track']['name']
                artist_name = track['track']['artists'][0]['name']
                search_query = f"{track_name} - {artist_name}"

                # Vyhledání skladby na YouTube Music
                search_response = youtube.search().list(
                    q=search_query,
                    part='id,snippet',
                    type='video',
                    maxResults=1,
                    key=API_KEY
                ).execute()

                # Zpracování výsledku vyhledávání
                if search_response['items']:
                    video_id = search_response['items'][0]['id']['videoId']
                    print(f"Nalezena skladba na YouTube: {search_query} ({video_id})")

                    # Přidání skladby do playlistu na YouTube Music
                    playlist_item_response = youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                }
                            }
                        }
                    ).execute()

                    print(f"Skladba přidána do playlistu: {track_name}")

                    # Aktualizace stavu
                    progress[playlist_title]["last_track_index"] = i + 1
                    with open("progress.json", "w") as f:
                        json.dump(progress, f)
                else:
                    print(f"Skladba nenalezena na YouTube: {search_query}")

            except HTTPError as e:
                print(f"Chyba YouTube API: {e}")
            except spotipy.SpotifyException as e:
                print(f"Chyba Spotify API: {e}")

    except HTTPError as e:
        print(f"Chyba YouTube API: {e}")
    except spotipy.SpotifyException as e:
        print(f"Chyba Spotify API: {e}")