import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy

import ytmusicauth
from song import Song

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID") or ""
CLIENT_SECRET = os.getenv("CLIENT_SECRET") or ""
REDIRECT_URI = os.getenv("REDIRECT_URI") or ""
SCOPE = os.getenv("SCOPE")

class Spotify:
    def __init__(self, client_id, client_secret, redirect_uri, scope):
        self.spotify_client_id = client_id
        self.spotify_client_secret = client_secret
        self.spotify_redirect_uri = redirect_uri
        self.spotify_scope = scope
        self.sp: spotipy.Spotify
        self.sp = None
        # self.content: list[Song] = []
        # self.content_name = lambda x: f".spotify_{x}.json"



    def login(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=self.spotify_client_id,
                                                            client_secret=self.spotify_client_secret,
                                                            redirect_uri=self.spotify_redirect_uri,
                                                            scope=self.spotify_scope))
        return self.sp

    def get_saved_tracks(self):
        results = self.sp.current_user_saved_tracks()
        tracks = []
        for idx, item in enumerate(results['items']):
            track = item['track']
            tracks.append({
                'index': idx,
                'artist': track['artists'][0]['name'],
                'title': track['name']
            })
        return tracks


    def get_playlists(self):
        playlists = self.sp.current_user_playlists()
        print("Playlists:",playlists)
        return [{'name': playlist['name'], 'id': playlist['id']} for playlist in playlists['items']]

    def get_playlist_tracks(self, playlist_id):
        results = self.sp.playlist_tracks(playlist_id)
        tracks = []
        for item in results.items:
            track = item['track']
            tracks.append(Song(
                title=track['name'],
                artist=track['artists'][0]['name'],
                isrc=track.get('external_ids', {}).get('isrc'),
            ))