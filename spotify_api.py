"""
Spotify API Module
Handles API calls to fetch top tracks and artists
"""


class SpotifyAPI:
    """Manages Spotify API interactions"""

    # Time range mapping
    TIME_RANGES = {
        "This Week": "short_term",
        "This Month": "medium_term",
        "Last 6 Months": "long_term"
    }

    def __init__(self, sp_client):
        """
        Initialize SpotifyAPI with authenticated client

        Args:
            sp_client: Authenticated Spotipy client
        """
        self.sp = sp_client

    def get_top_artists(self, time_range="medium_term", limit=5):
        """
        Fetch top artists for the user

        Args:
            time_range (str): One of 'short_term', 'medium_term', 'long_term'
            limit (int): Number of artists to fetch (default 5)

        Returns:
            list: List of artist dictionaries with name, image, and genres
        """
        try:
            results = self.sp.current_user_top_artists(
                time_range=time_range,
                limit=limit
            )

            artists = []
            for item in results['items']:
                artist_data = {
                    'name': item['name'],
                    'genres': ', '.join(item['genres']) if item['genres'] else 'N/A',
                    'image': item['images'][0]['url'] if item['images'] else None,
                    'popularity': item['popularity'],
                    'url': item['external_urls'].get('spotify', '#')
                }
                artists.append(artist_data)

            return artists
        except Exception as e:
            print(f"Error fetching top artists: {e}")
            return []

    def get_top_tracks(self, time_range="medium_term", limit=5):
        """
        Fetch top tracks for the user

        Args:
            time_range (str): One of 'short_term', 'medium_term', 'long_term'
            limit (int): Number of tracks to fetch (default 5)

        Returns:
            list: List of track dictionaries with name, artist, album, and image
        """
        try:
            results = self.sp.current_user_top_tracks(
                time_range=time_range,
                limit=limit
            )

            tracks = []
            for item in results['items']:
                track_data = {
                    'name': item['name'],
                    'artist': ', '.join([artist['name'] for artist in item['artists']]),
                    'album': item['album']['name'],
                    'image': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'popularity': item['popularity'],
                    'url': item['external_urls'].get('spotify', '#'),
                    'duration_ms': item['duration_ms']
                }
                tracks.append(track_data)

            return tracks
        except Exception as e:
            print(f"Error fetching top tracks: {e}")
            return []

    def get_user_profile(self):
        """
        Fetch current user profile information

        Returns:
            dict: User profile data with display name and image
        """
        try:
            user = self.sp.current_user()
            return {
                'name': user.get('display_name', 'User'),
                'image': user['images'][0]['url'] if user.get('images') else None,
                'email': user.get('email', 'N/A')
            }
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return {'name': 'User', 'image': None, 'email': 'N/A'}