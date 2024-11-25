from ytmusicauth import YouTubeMusic

def test_youtube_music_initialization():
    yt_music = YouTubeMusic('credentials.json', ['https://www.googleapis.com/auth/youtube'], 'youtube', 'v3')
    assert yt_music.youtube is not None