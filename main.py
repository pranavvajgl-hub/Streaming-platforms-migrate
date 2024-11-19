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

# SIGN IN TO YOUTUBE MUSIC
youtube = ytmusicauth.get_authenticated_service()
youtube_playlists = youtube.playlists().list(part="snippet", mine=True).execute()

# PLAYLIST COMPARISON
for spotify_playlist in spotify_playlists:
    for youtube_playlist in youtube_playlists['items']:
        if spotify_playlist['name'] == youtube_playlist['snippet']['title']:

            '''
            Here we are getting list of tracks on both platforms
            '''
            spotify_tracks = spotify_client.get_playlist_tracks(spotify_playlist['id'])
            youtube_tracks = youtube.playlistItems().list(
                part="snippet", playlistId=youtube_playlist['id'], maxResults=100
            ).execute()

            '''
            Comparison magic
            '''
            for spotify_track in spotify_tracks['items']:
                spotify_track.get_youtube_id(youtube)
                found = False
                for youtube_track in youtube_tracks['items']:
                    #and spotify_track.artist == youtube_track["snippet"]["videoOwnerChannelTitle"]
                    #pripis to nahore, jestli to nepujde...
                    if spotify_track.youtube_id == youtube_track['snippet']['resourceId']['title']:
                        found = True
                        break
                    if not found:
                        request = youtube.playlistItems().insert(
                            part="snippet",
                            body={
                                "snippet": {
                                    "playlistId": youtube_playlist['id'],
                                    "resourceId": {
                                        "kind": "youtube#video",
                                        "videoId": spotify_track.get_video_id(youtube)
                                    }
                                }
                            }
                        )
                        response = request.execute()