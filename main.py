import json
import os
from urllib.error import HTTPError
import time
import spotipy
from dotenv import load_dotenv
from spotauth import Spotify
from ytmusicauth import YouTubeMusic

def last_trace(filename="progress.json"):
    try:
        with open(filename, "r") as f:
            loaded_progress = json.load(f)
    except FileNotFoundError:
        loaded_progress = {}
    return loaded_progress

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

# Loading the state of last usage
progress = last_trace()

try:
    playlists = sp.current_user_playlists()
except spotipy.SpotifyException as e:
    print(f"Error with Spotify API: {e}")
    exit()

# In every playlist
for playlist in playlists['items']:
    try:
        # See if the album does exist
        playlist_title = playlist['name']
        if playlist_title in progress:
            playlist_id = progress[playlist_title]["id"]
            last_track_index = progress[playlist_title]["last_track_index"]
            print(f"Playlist '{playlist_title}' does exist. Continue with index {last_track_index}.")
        else:
            # Creating a new album
            time.sleep(1)
            playlist_response = youtube.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": playlist_title,
                        "description": f"Playlist form Spotify",
                    },
                    "status": {
                        "privacyStatus": "private"
                    }
                },
                key=API_KEY
            ).execute()

            playlist_id = playlist_response['id']
            print(f"Playlist created on YouTube: {playlist_title} ({playlist_id})")
            last_track_index = 0
            progress[playlist_title] = {"id": playlist_id, "last_track_index": last_track_index}


        tracks = sp.playlist_tracks(playlist['id'])
        search_cache = {}

        for i, track in enumerate(tracks['items']):
            search_response = None
            search_query = None
            track_name = None

            # Skip last track
            if i < last_track_index:
                continue
            try:
                try:
                    # Track info on spotify
                    track_name = track['track']['name']
                    artist_name = track['track']['artists'][0]['name']
                    search_query = f"{track_name} - {artist_name}"
                    # Search on YTMusic
                    if search_query in search_cache:
                        search_response = search_cache[search_query]
                        print(f"Result from search is form cache: {search_query}")
                    else:
                        search_response = youtube.search().list(
                            q=search_query,
                            part='id,snippet',
                            type='video',
                            maxResults=1,
                            key=API_KEY
                        ).execute()
                        search_cache[search_query] = search_response
                except HTTPError as e:
                    if "quotaExceeded" in str(e):
                        print("You have exceeded your quota for searching.")
                    else:
                        print(f"Error with YouTube API: {e}")
                        raise

                # Adding playlist into YTMusic found on Spotify
                if search_response['items']:
                    video_id = search_response['items'][0]['id']['videoId']
                    print(f"Track found on YouTube: {search_query} ({video_id})")

                    # Adding song into playlist
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
                        },
                        key=API_KEY
                    ).execute()
                    youtube_music.update_progress(progress, playlist_title, i)
                    print(f"Track: {track_name} added into playlist {playlist_id}")
                else:
                    print(f"Track found on YouTube: {search_query}")

            except HTTPError as e:
                print(f"Error with YouTube API: {e}")
            except spotipy.SpotifyException as e:
                print(f"Error with Spotify API: {e}")
    except HTTPError as e:
        print(f"Error with YouTube API: {e}")
    except spotipy.SpotifyException as e:
        print(f"Error with Spotify API: {e}")