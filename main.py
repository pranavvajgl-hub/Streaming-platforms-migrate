import json
import os
import time
import logging
import spotipy
from urllib.error import HTTPError
from dotenv import load_dotenv
from spotauth import Spotify
from ytmusicauth import YouTubeMusic


def get_last_progress(filename="progress.json"):
    try:
        with open(filename, "r") as f:
            loaded_progress = json.load(f)
    except FileNotFoundError:
        loaded_progress = {}
    return loaded_progress

def save_progress(progress, filename="progress.json"):
    with open("progress.json", "w") as f:
        json.dump(progress, f)

load_dotenv()

logging.basicConfig(filename='sync.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Config for Spotify API
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

# State of previously added songs/albums
progress = get_last_progress()

# Loading Spotify playlists:
playlists = spotify.get_playlists()

# In every playlist
for playlist in playlists['items']:
    try:
        # See if the album does exist in Spotify
        playlist_title = playlist['name']
        if playlist_title in progress:
            playlist_id = progress[playlist_title]["id"]
            last_track_index = progress[playlist_title]["last_track_index"]
            print(f"Playlist '{playlist_title}' does exist. Continue with index {last_track_index}.")
            logging.info(f"Playlist '{playlist_title}' does exist. Continue with index {last_track_index}.")
        else:
            # Creating a new album on YT Music
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
            logging.info(f"Playlist created on YouTube: {playlist_title} ({playlist_id})")

            # Saving progress
            last_track_index = 0
            progress[playlist_title] = {"id": playlist_id, "last_track_index": last_track_index}
            save_progress(progress)
            logging.info(f"Progress saved on index: {progress[playlist_title]}")

        # Initialization of tracks in playlist
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
                        logging.info(f"You have exceeded your quota for searching.")
                    else:
                        print(f"Error with YouTube API: {e}")
                        logging.info(f"Error with YouTube API: {e}")
                        raise

                # Adding playlist into YTMusic found on Spotify
                if search_response['items']:
                    video_id = search_response['items'][0]['id']['videoId']
                    print(f"Track found on YouTube: {search_query} ({video_id})")

                    max_retries = 3
                    retries = 0
                    while retries < max_retries:
                        try:
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
                            print(f"Track: {track_name} added into playlist {playlist_id}")
                            logging.info(f"Track: {track_name} added into playlist {playlist_id}")
                            # Saving progress
                            progress[playlist_title]["last_track_index"] = i + 1
                            save_progress(progress)

                        except HTTPError as e:
                            if e.resp.status == 409 and "SERVICE_UNAVAILABLE" in str(e):
                                retries += 1
                                print(f"Error adding song (attempt {retries}/{max_retries}): {e}")
                                logging.info(f"Error adding song (attempt {retries}/{max_retries}): {e}")
                                time.sleep(2)
                            else:
                                print(f"Error with YouTube API: {e}")
                                logging.info(f"Error with YouTube API: {e}")
                                raise

                        break

                    if retries == max_retries:
                        print(f"Failed to add after {max_retries} retries")
                        logging.info(f"Failed to add after {max_retries} retries")
                else:
                    print(f"Track found on YouTube: {search_query}")
                    logging.info(f"Track found on YouTube: {search_query}")

            except HTTPError as e:
                print(f"Error with YouTube API: {e}")
                logging.info(f"Error with YouTube API: {e}")
            except spotipy.SpotifyException as e:
                print(f"Error with Spotify API: {e}")
                logging.info(f"Error with Spotify API: {e}")

    except HTTPError as e:
        print(f"Error with YouTube API: {e}")
        logging.info(f"Error with YouTube API: {e}")
    except spotipy.SpotifyException as e:
        print(f"Error with Spotify API: {e}")
        logging.info(f"Error with Spotify API: {e}")