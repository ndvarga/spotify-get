Spotify playlist/track downloader CLI. It looks up tracks on YouTube (via `yt-dlp`) and downloads audio.

## Setup
- Python 3.9+ recommended.
- Install deps: `pip install -r requirements.txt` (or via package install below).
- Provide Spotify API creds (choose one):
  - **Option 1**: Create a `.env` file in your home directory (`~/.env` or `C:\Users\YourName\.env`):
    ```
    SPOTIFY_CLIENT_ID=your_spotify_client_id
    SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
    ```
    This works globally after package installation.
  - **Option 2**: Create a `.env` file in the project directory (for development).
  - **Option 3**: Set them as environment variables in your shell profile.
- Install the CLI (from repo root):
  - Editable: `python -m pip install -e .`
  - Regular: `python -m pip install .`
  This exposes the `spotify-get` command on your PATH.

## Usage
CLI entry point (works from any directory after install):
```
spotify-get <playlist_url_or_id> [options]
spotify-get --track <track_url_or_id> [options]
```

Options:
- `-f, --audio-format` (default `mp3`): audio format for `yt-dlp`.
- `-o, --output` (default `downloads`): directory where files are saved.
- `-t, --threads` (default `4`): max concurrent downloads.

Examples:
```
# Download a Spotify playlist
spotify-get https://open.spotify.com/playlist/your_id

# Download a single Spotify track
spotify-get --track https://open.spotify.com/track/your_id

# SoundCloud playlist or track
spotify-get https://soundcloud.com/playlist-url
spotify-get --track https://soundcloud.com/track-url

# Custom format/output and concurrency
spotify-get https://open.spotify.com/playlist/your_id -f m4a -o downloads -t 6
```

Notes:
- Output template: `<output>/<title>.<ext>` as resolved by `yt-dlp`.
- Spotify lookups search YouTube via `ytsearch:<artist> <title>`.
