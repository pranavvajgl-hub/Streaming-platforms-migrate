from spotauth import Spotify
import spotipy

def test_spotify_initialization():
    spotify = Spotify("test_client_id", "test_client_secret", "test_redirect_uri", "test_scope")
    assert isinstance(spotify.sp, spotipy.Spotify)