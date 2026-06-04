"""
Spotify Dashboard
Main GUI application for displaying top Spotify artists and songs
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import requests
from urllib.parse import urljoin
import threading

from spotify_auth import SpotifyAuthenticator
from spotify_api import SpotifyAPI


class SpotifyDashboard:
    """Main GUI application for Spotify Dashboard"""

    def __init__(self, root):
        self.root = root
        self.root.title("Spotify Dashboard")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)

        # Initialize variables
        self.sp_client = None
        self.sp_api = None
        self.current_time_range = "medium_term"
        self.loading = False

        # Configure styles
        self.setup_styles()

        # Create UI
        self.create_ui()

        # Try to authenticate
        self.authenticate()

    def setup_styles(self):
        """Setup custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors (Spotify Green theme)
        self.bg_color = "#121212"
        self.fg_color = "#FFFFFF"
        self.spotify_green = "#1DB954"
        self.secondary_bg = "#282828"

        self.root.configure(bg=self.bg_color)

    def create_ui(self):
        """Create the main UI layout"""
        # Top frame - Header and controls
        top_frame = tk.Frame(self.root, bg=self.spotify_green, height=60)
        top_frame.pack(fill=tk.X, pady=0)

        # Title
        title_label = tk.Label(
            top_frame,
            text="🎵 Spotify Dashboard",
            font=("Arial", 20, "bold"),
            bg=self.spotify_green,
            fg=self.bg_color
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=10)

        # Control frame - Time range and refresh buttons
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(fill=tk.X, padx=20, pady=15)

        time_label = tk.Label(
            control_frame,
            text="Select Time Range:",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.fg_color
        )
        time_label.pack(side=tk.LEFT, padx=5)

        # Time range buttons
        self.time_buttons = {}
        for period_name, period_code in [("This Week", "short_term"),
                                          ("This Month", "medium_term"),
                                          ("Last 6 Months", "long_term")]:
            btn = tk.Button(
                control_frame,
                text=period_name,
                font=("Arial", 10),
                bg=self.spotify_green if period_code == self.current_time_range else self.secondary_bg,
                fg=self.bg_color if period_code == self.current_time_range else self.fg_color,
                command=lambda code=period_code, name=period_name: self.change_time_range(code, name),
                relief=tk.FLAT,
                padx=15,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.time_buttons[period_code] = btn

        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            font=("Arial", 10),
            bg=self.spotify_green,
            fg=self.bg_color,
            command=self.refresh_data,
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create two columns
        artists_frame = tk.Frame(content_frame, bg=self.secondary_bg)
        artists_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        tracks_frame = tk.Frame(content_frame, bg=self.secondary_bg)
        tracks_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Artists section
        artists_title = tk.Label(
            artists_frame,
            text="Top 5 Artists",
            font=("Arial", 14, "bold"),
            bg=self.secondary_bg,
            fg=self.spotify_green
        )
        artists_title.pack(padx=10, pady=10)

        self.artists_container = tk.Frame(artists_frame, bg=self.secondary_bg)
        self.artists_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tracks section
        tracks_title = tk.Label(
            tracks_frame,
            text="Top 5 Songs",
            font=("Arial", 14, "bold"),
            bg=self.secondary_bg,
            fg=self.spotify_green
        )
        tracks_title.pack(padx=10, pady=10)

        self.tracks_container = tk.Frame(tracks_frame, bg=self.secondary_bg)
        self.tracks_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 9),
            bg=self.secondary_bg,
            fg=self.fg_color,
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

    def authenticate(self):
        """Authenticate with Spotify API"""
        self.set_status("Authenticating with Spotify...")
        threading.Thread(target=self._authenticate_thread, daemon=True).start()

    def _authenticate_thread(self):
        """Run authentication in background thread"""
        try:
            auth = SpotifyAuthenticator()
            self.sp_client = auth.get_spotify_client()
            self.sp_api = SpotifyAPI(self.sp_client)

            # Verify authentication
            user = self.sp_api.get_user_profile()
            self.set_status(f"Authenticated as {user['name']}. Loading data...")

            # Load initial data
            self.load_data()
        except Exception as e:
            self.set_status(f"Authentication failed: {str(e)}")
            messagebox.showerror("Authentication Error", f"Failed to authenticate:\n{str(e)}")

    def change_time_range(self, time_code, display_name):
        """Change the time range and reload data"""
        self.current_time_range = time_code

        # Update button states
        for code, btn in self.time_buttons.items():
            if code == time_code:
                btn.config(bg=self.spotify_green, fg=self.bg_color)
            else:
                btn.config(bg=self.secondary_bg, fg=self.fg_color)

        self.load_data()

    def load_data(self):
        """Load top artists and tracks in background thread"""
        if not self.sp_api:
            messagebox.showerror("Error", "Not authenticated with Spotify")
            return

        self.loading = True
        self.set_status("Loading data...")
        threading.Thread(target=self._load_data_thread, daemon=True).start()

    def _load_data_thread(self):
        """Load data in background thread"""
        try:
            artists = self.sp_api.get_top_artists(self.current_time_range, limit=5)
            tracks = self.sp_api.get_top_tracks(self.current_time_range, limit=5)

            self.root.after(0, self.display_artists, artists)
            self.root.after(0, self.display_tracks, tracks)
            self.set_status("Data loaded successfully")
        except Exception as e:
            self.set_status(f"Error loading data: {str(e)}")
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
        finally:
            self.loading = False

    def display_artists(self, artists):
        """Display top artists in the UI"""
        # Clear existing widgets
        for widget in self.artists_container.winfo_children():
            widget.destroy()

        for idx, artist in enumerate(artists, 1):
            self.create_artist_card(idx, artist)

    def display_tracks(self, tracks):
        """Display top tracks in the UI"""
        # Clear existing widgets
        for widget in self.tracks_container.winfo_children():
            widget.destroy()

        for idx, track in enumerate(tracks, 1):
            self.create_track_card(idx, track)

    def create_artist_card(self, rank, artist):
        """Create a card widget for an artist"""
        card = tk.Frame(self.artists_container, bg=self.bg_color, relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5)

        # Artist image and rank
        img_frame = tk.Frame(card, bg=self.bg_color, width=60, height=60)
        img_frame.pack(side=tk.LEFT, padx=10, pady=10)

        rank_label = tk.Label(
            img_frame,
            text=f"#{rank}",
            font=("Arial", 14, "bold"),
            bg=self.spotify_green,
            fg=self.bg_color,
            width=4,
            height=2
        )
        rank_label.pack()

        # Artist info
        info_frame = tk.Frame(card, bg=self.bg_color)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        name_label = tk.Label(
            info_frame,
            text=artist['name'],
            font=("Arial", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            wraplength=200,
            justify=tk.LEFT
        )
        name_label.pack(anchor=tk.W)

        genres_label = tk.Label(
            info_frame,
            text=f"Genres: {artist['genres']}",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#B0B0B0",
            wraplength=200,
            justify=tk.LEFT
        )
        genres_label.pack(anchor=tk.W)

        popularity_label = tk.Label(
            info_frame,
            text=f"Popularity: {artist['popularity']}%",
            font=("Arial", 9),
            bg=self.bg_color,
            fg=self.spotify_green
        )
        popularity_label.pack(anchor=tk.W)

    def create_track_card(self, rank, track):
        """Create a card widget for a track"""
        card = tk.Frame(self.tracks_container, bg=self.bg_color, relief=tk.RAISED, bd=1)
        card.pack(fill=tk.X, pady=5)

        # Rank
        rank_label = tk.Label(
            card,
            text=f"#{rank}",
            font=("Arial", 14, "bold"),
            bg=self.spotify_green,
            fg=self.bg_color,
            width=4
        )
        rank_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Track info
        info_frame = tk.Frame(card, bg=self.bg_color)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        name_label = tk.Label(
            info_frame,
            text=track['name'],
            font=("Arial", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            wraplength=250,
            justify=tk.LEFT
        )
        name_label.pack(anchor=tk.W)

        artist_label = tk.Label(
            info_frame,
            text=f"By: {track['artist']}",
            font=("Arial", 9),
            bg=self.bg_color,
            fg="#B0B0B0",
            wraplength=250,
            justify=tk.LEFT
        )
        artist_label.pack(anchor=tk.W)

        album_label = tk.Label(
            info_frame,
            text=f"Album: {track['album']}",
            font=("Arial", 9),
            bg=self.bg_color,
            fg=self.spotify_green,
            wraplength=250,
            justify=tk.LEFT
        )
        album_label.pack(anchor=tk.W)

    def refresh_data(self):
        """Refresh the data"""
        if not self.loading:
            self.load_data()
        else:
            messagebox.showinfo("Info", "Already loading data...")

    def set_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SpotifyDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()