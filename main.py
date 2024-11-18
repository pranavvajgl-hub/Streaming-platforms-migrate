import os
from dotenv import load_dotenv
import ytmusicauth
import spotauth
from spotauth import Spotify, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json
import sys
from typing import Any
from song import Song

from symtable import Class
import requests

# SING INTO SPOTIFY
spotify_client = Spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
sp = spotify_client.login()
spotify_playlists = spotify_client.get_playlists()

# SIGN INTO YTMUSIC
youtube = ytmusicauth.get_authenticated_service()
youtube_playlists = youtube.playlists().list(part="snippet", mine=True).execute()

for spotify_playlist in spotify_playlists:
    for youtube_playlist in youtube_playlists['items']:
        if spotify_playlist['name'] == youtube_playlist['snippet']['title']:
            spotify_tracks = spotify_client.get_playlist_tracks()