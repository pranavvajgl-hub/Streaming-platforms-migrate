class Song:
    def __init__(self, title: str, artist: str, isrc:str) -> None:
        self.title = title
        self.artist = artist
        self.isrc = isrc
        self.youtube_id = None

    def get_dictionary(self) -> dict[str, str]:
        return {
            "title": self.title,
            "artist": self.artist,
            "isrc": self.isrc
        }

    def get_youtube_id(self, youtube):
        """
        Only for YouTube Music. THis searches for YouTube ID.
        """
        request = youtube.search().list(
            part='snippet',
            q=f"{self.title} {self.artist}",
            type='video'
        )
        response = request.execute()
        if response['items']:
            self.youtube_id = response['items'][0]['snippet']['id']['videoId']
            print(f"Video ID found for this song: {self.title}: {self.youtube_id}")
        else:
            print(f"Video ID for this song: {self.title}, did not found" )