"""
Spotify Authentication Module
Handles OAuth 2.0 authentication with Spotify API
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


class SpotifyAuthenticator:
    """Manages Spotify OAuth authentication"""

    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file"
            )

        self.scope = [
            "user-top-read",
            "user-read-private",
            "user-read-email"
        ]

    def get_spotify_client(self):
        """
        Authenticate and return a Spotipy client instance

        Returns:
            spotipy.Spotify: Authenticated Spotify client
        """
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=".spotifyauth_cache"
        )

        return spotipy.Spotify(auth_manager=auth_manager)

    def is_authenticated(self):
        """
        Check if user is already authenticated

        Returns:
            bool: True if cached token exists, False otherwise
        """
        return os.path.exists(".spotifyauth_cache")