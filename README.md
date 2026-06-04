# Spotify Dashboard

A desktop application that displays your top 5 most listened artists and songs from Spotify with time period filtering (This Week, This Month, Last 6 Months).

## Features

- 🎵 Display top 5 most listened artists
- 🎶 Display top 5 most listened songs
- 📅 Filter by time period:
  - This Week (short_term)
  - This Month (medium_term)
  - Last 6 Months (long_term)
- 🔐 Secure OAuth authentication with Spotify
- 💻 Clean, user-friendly GUI

## Requirements

- Python 3.8+
- Windows 10/11
- Spotify Account (Premium or Free)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/d1ovoo/spotify-dashboard.git
cd spotify-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a Spotify Developer Application:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Accept the terms and create the app
   - Copy your **Client ID** and **Client Secret**

4. Create a `.env` file in the project root:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

## Usage

Run the application:
```bash
python main.py
```

The GUI will open with buttons to authenticate with Spotify and display your top stats.

## Project Structure

```
spotify-dashboard/
├── main.py                 # Main GUI application
├── spotify_auth.py         # Spotify authentication logic
├── spotify_api.py          # Spotify API interactions
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
└── README.md              # This file
```

## License

MIT License

## Support

For issues or questions, please create an issue on GitHub.