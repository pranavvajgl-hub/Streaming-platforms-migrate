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

def compare_playlists(spotify_client, youtube_client, spotify_playlists, youtube_playlists):
    """
    Compares and syncs playlists from Spotify and YouTube
    """
    for spotify_playlist in spotify_playlists:
        for youtube_playlist in youtube_playlists['items']:
            if spotify_playlist['name'] == youtube_playlist['snippet']['title']:
                compare_tracks(spotify_client, youtube_client, spotify_playlist, youtube_playlist)

def compare_tracks(spotify_client, youtube_client, spotify_playlist, youtube_playlist):
    """
    Compares tracks in searched playlists on both platforms
    """
    spotify_tracks = spotify_client.get_playlist_tracks(spotify_playlist['id'])
    youtube_tracks = youtube_client.playlistItems().list(
        part="snippet",playlistId=youtube_playlist['id'], maxResults=100
    ).execute()
    for spotify_track in spotify_tracks['items']:
        spotify_track.get_youtube_id(youtube_client)
        found = False
        for youtube_track in youtube_tracks['items']:
            if spotify_track.youtube_id == youtube_track['snippet']['resourceId']['videoId']:
                found = True
                break
        if not found:
            request = youtube_client.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": youtube_playlist['id'],
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": spotify_track.video_id
                        }
                    }
                }
            )
            response = request.execute()



# SING INTO SPOTIFY
spotify_client = Spotify(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE)
sp = spotify_client.login()
spotify_playlists = spotify_client.get_playlists()

# SIGN IN TO YOUTUBE MUSIC
youtube_client = ytmusicauth.get_authenticated_service()
youtube_playlists = youtube_client.playlists().list(part="snippet", mine=True).execute()

compare_playlists(spotify_client, youtube_client, spotify_playlists, youtube_playlists)