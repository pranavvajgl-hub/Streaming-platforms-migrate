# Streaming-platforms-migrate

This Python script allows you to migrate your playlists between Spotify and YouTube Music using API.

This script was created due to the difference in playback quality between platforms.

## Features

* Migrates playlists from Spotify to YouTube Music.
* Handles missing songs gracefully.
* Provides logging for tracking progress and errors.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/pranavvajgl-hub/Streaming-platforms-migrate.git
   
2. **Create virtual environment**

    ````bash
   python3 -m venv venv
   source venv/bin/activate

3. **Install the required packages**

    ```bash
   pip install -r requirements.txt
   
4. **Or install individual packages**

    ```bash
    pip install spotipy
    pip install python-dotenv
    pip install google-api-python-client
    pip install google-auth-oauthlib

5. **Set up Spotify API**

* Sign in to your account on [Spotify Developers](https://developer.spotify.com/).
* In your dashboard click on Create App and fill up necessary boxes.
* Set redirect uri to:
    ```bash
  https://accounts.spotify.com/api/token
  http://127.0.0.1:9090
  http://localhost
  http://localhost:8888/callback

* In column "Which API/SDKs are you planning to use?" choose **Web API**
* After you save the app, you should obtain your `Client ID`, `Client Secret`
* Create `.env` file and add the following variables:
    ````bash
    CLIENT_ID=your_spotify_client_id
    CLIENT_SECRET=your_spotify_client_secret
    REDIRECT_URI=your_spotify_redirect_uri
    SCOPE=your_spotify_scopes

* For `REDIRECT_URI` and for `SCOPE` add these parameters:
    ````bash
    REDIRECT_URI='http://localhost:8888/callback'
    SCOPE="user-library-read playlist-read-private playlist-read-collaborative"

6. **Set up YouTube Music API**

* Sign in to your account on [Google Cloud Console](https://console.cloud.google.com/)
* Create new project and in section `Library` add `YouTube Data API v3`
* In the left tray click on **Credentials**, there in the section **API Keys** create your API key and add it in to the `.env` file
    ````bash
    API_KEY=your_api_key
  
* In the end your `.env` file should look like this:
    ````bash
    CLIENT_ID=your_spotify_client_id
    CLIENT_SECRET=your_spotify_client_secret
    REDIRECT_URI=your_spotify_redirect_uri
    SCOPE=your_spotify_scopes
    API_KEY=your_api_key

* In **Credentials** choose **OAuth consent screen** and obtain your `credentials.json`. Place this file in to the project repository.

## Usage

1. **Run the script:**

    ````bash
    python start.py

2. **Follow the on-screen instructions:**

* The script will prompt you to authorize access to your Spotify and YouTube Music accounts.
* Playlists should automatically convert into YT Music

**Warning:** Google limits the quota for YouTube Music API to 10,000 queries per day.

## Contributing

**Contributions are welcome! Feel free to open an issue or submit a pull request.**

## License

This project is licensed under the MIT License.

